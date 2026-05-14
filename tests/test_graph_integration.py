"""Integration tests: build_diff_graph + graph_reporter together."""
import io
import tempfile
import os

from envdiff.parser import parse_env_file
from envdiff.differ_graph import build_diff_graph
from envdiff.graph_reporter import format_graph_report


def _write(tmp_dir: str, name: str, content: str) -> str:
    path = os.path.join(tmp_dir, name)
    with open(path, "w") as f:
        f.write(content)
    return path


def test_integration_two_identical_files():
    with tempfile.TemporaryDirectory() as d:
        p1 = _write(d, ".env.a", "FOO=bar\nBAZ=qux\n")
        p2 = _write(d, ".env.b", "FOO=bar\nBAZ=qux\n")
        envs = {p1: parse_env_file(p1), p2: parse_env_file(p2)}
        graph = build_diff_graph(envs)
        assert graph.inconsistent_keys() == []
        report = format_graph_report(graph, color=False)
        assert "all consistent" in report


def test_integration_mismatched_values():
    with tempfile.TemporaryDirectory() as d:
        p1 = _write(d, ".env.dev", "DB=localhost\nDEBUG=true\n")
        p2 = _write(d, ".env.prod", "DB=prod.host\nDEBUG=false\n")
        envs = {"dev": parse_env_file(p1), "prod": parse_env_file(p2)}
        graph = build_diff_graph(envs)
        assert "DB" in graph.inconsistent_keys()
        assert "DEBUG" in graph.inconsistent_keys()


def test_integration_missing_key_detected():
    with tempfile.TemporaryDirectory() as d:
        p1 = _write(d, ".env.a", "FOO=1\nBAR=2\n")
        p2 = _write(d, ".env.b", "FOO=1\n")
        envs = {"a": parse_env_file(p1), "b": parse_env_file(p2)}
        graph = build_diff_graph(envs)
        assert "BAR" in graph.missing_in("b")
        assert graph.missing_in("a") == []


def test_integration_report_shows_missing_source():
    with tempfile.TemporaryDirectory() as d:
        p1 = _write(d, ".env.x", "ONLY_IN_X=yes\nSHARED=val\n")
        p2 = _write(d, ".env.y", "SHARED=val\n")
        envs = {"x": parse_env_file(p1), "y": parse_env_file(p2)}
        graph = build_diff_graph(envs)
        report = format_graph_report(graph, color=False)
        assert "MISSING" in report
        assert "ONLY_IN_X" in report


def test_integration_three_sources():
    with tempfile.TemporaryDirectory() as d:
        p1 = _write(d, "a.env", "KEY=1\n")
        p2 = _write(d, "b.env", "KEY=1\n")
        p3 = _write(d, "c.env", "KEY=2\n")
        envs = {
            "a": parse_env_file(p1),
            "b": parse_env_file(p2),
            "c": parse_env_file(p3),
        }
        graph = build_diff_graph(envs)
        assert len(graph.source_names) == 3
        assert "KEY" in graph.inconsistent_keys()
