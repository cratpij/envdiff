"""Tests for envdiff.differ_graph."""
import pytest
from envdiff.differ_graph import GraphNode, DiffGraph, build_diff_graph


# ---------------------------------------------------------------------------
# GraphNode
# ---------------------------------------------------------------------------

def test_graph_node_consistent_single_value():
    node = GraphNode(key="FOO", sources=["a", "b"], values={"a": "1", "b": "1"})
    assert node.is_consistent is True


def test_graph_node_inconsistent_different_values():
    node = GraphNode(key="FOO", sources=["a", "b"], values={"a": "1", "b": "2"})
    assert node.is_consistent is False


def test_graph_node_consistent_single_source():
    node = GraphNode(key="FOO", sources=["a"], values={"a": "hello"})
    assert node.is_consistent is True


# ---------------------------------------------------------------------------
# build_diff_graph
# ---------------------------------------------------------------------------

def _envs():
    return {
        "dev": {"DB_HOST": "localhost", "DEBUG": "true", "SECRET": "dev-secret"},
        "prod": {"DB_HOST": "prod.db", "DEBUG": "false", "PORT": "443"},
    }


def test_build_graph_all_keys_present():
    graph = build_diff_graph(_envs())
    assert set(graph.all_keys()) == {"DB_HOST", "DEBUG", "SECRET", "PORT"}


def test_build_graph_source_names():
    graph = build_diff_graph(_envs())
    assert graph.source_names == ["dev", "prod"]


def test_build_graph_inconsistent_keys():
    graph = build_diff_graph(_envs())
    assert set(graph.inconsistent_keys()) == {"DB_HOST", "DEBUG"}


def test_build_graph_missing_in_dev():
    graph = build_diff_graph(_envs())
    assert graph.missing_in("dev") == ["PORT"]


def test_build_graph_missing_in_prod():
    graph = build_diff_graph(_envs())
    assert graph.missing_in("prod") == ["SECRET"]


def test_build_graph_values_stored_correctly():
    graph = build_diff_graph(_envs())
    assert graph.nodes["DB_HOST"].values == {"dev": "localhost", "prod": "prod.db"}


def test_build_graph_summary_with_inconsistency():
    graph = build_diff_graph(_envs())
    summary = graph.summary()
    assert "inconsistent" in summary
    assert "2" in summary


def test_build_graph_summary_all_consistent():
    envs = {"a": {"FOO": "bar"}, "b": {"FOO": "bar"}}
    graph = build_diff_graph(envs)
    assert "all consistent" in graph.summary()


def test_build_graph_empty_envs():
    graph = build_diff_graph({})
    assert graph.all_keys() == []
    assert graph.source_names == []


def test_build_graph_single_source():
    graph = build_diff_graph({"only": {"A": "1", "B": "2"}})
    assert len(graph.all_keys()) == 2
    assert graph.inconsistent_keys() == []
