"""Tests for envdiff.inheritor."""

from __future__ import annotations

import pytest

from envdiff.inheritor import (
    InheritanceResult,
    inherit_envs,
    inherit_env_files,
)


# ---------------------------------------------------------------------------
# inherit_envs
# ---------------------------------------------------------------------------

def test_inherit_envs_child_wins_on_conflict():
    parent = {"A": "parent_a", "B": "parent_b"}
    child = {"A": "child_a", "C": "child_c"}
    result = inherit_envs(parent, child)
    assert result.resolved["A"] == "child_a"


def test_inherit_envs_parent_fills_missing_keys():
    parent = {"A": "1", "B": "2"}
    child = {"C": "3"}
    result = inherit_envs(parent, child)
    assert result.resolved["A"] == "1"
    assert result.resolved["B"] == "2"
    assert result.resolved["C"] == "3"


def test_inherit_envs_inherited_keys():
    parent = {"X": "x", "Y": "y"}
    child = {"Y": "override"}
    result = inherit_envs(parent, child)
    assert result.inherited_keys == ["X"]


def test_inherit_envs_overridden_keys():
    parent = {"A": "1", "B": "2"}
    child = {"A": "99"}
    result = inherit_envs(parent, child)
    assert result.overridden_keys == ["A"]


def test_inherit_envs_child_only_keys():
    parent = {"A": "1"}
    child = {"B": "2", "C": "3"}
    result = inherit_envs(parent, child)
    assert result.child_only_keys == ["B", "C"]


def test_inherit_envs_empty_parent():
    result = inherit_envs({}, {"A": "1"})
    assert result.resolved == {"A": "1"}
    assert result.inherited_keys == []
    assert result.child_only_keys == ["A"]


def test_inherit_envs_empty_child():
    result = inherit_envs({"A": "1"}, {})
    assert result.resolved == {"A": "1"}
    assert result.inherited_keys == ["A"]
    assert result.child_only_keys == []


def test_inherit_envs_both_empty():
    result = inherit_envs({}, {})
    assert result.resolved == {}
    assert result.inherited_keys == []
    assert result.overridden_keys == []
    assert result.child_only_keys == []


def test_inherit_envs_paths_stored():
    result = inherit_envs({}, {}, parent_path="base.env", child_path="dev.env")
    assert result.parent_path == "base.env"
    assert result.child_path == "dev.env"


def test_summary_contains_counts():
    parent = {"A": "1", "B": "2"}
    child = {"B": "override", "C": "3"}
    result = inherit_envs(parent, child)
    s = result.summary()
    assert "inherited" in s
    assert "overridden" in s
    assert "child-only" in s


# ---------------------------------------------------------------------------
# inherit_env_files
# ---------------------------------------------------------------------------

def test_inherit_env_files_reads_files(tmp_path):
    parent = tmp_path / "parent.env"
    child = tmp_path / "child.env"
    parent.write_text("BASE=1\nSHARED=parent\n")
    child.write_text("SHARED=child\nEXTRA=2\n")

    result = inherit_env_files(str(parent), str(child))
    assert result.resolved["BASE"] == "1"
    assert result.resolved["SHARED"] == "child"
    assert result.resolved["EXTRA"] == "2"
    assert "BASE" in result.inherited_keys
    assert "SHARED" in result.overridden_keys
    assert "EXTRA" in result.child_only_keys
