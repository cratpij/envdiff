"""Tests for envdiff.sorter module."""

import pytest
from envdiff.sorter import (
    sort_keys_alphabetically,
    group_keys_by_prefix,
    sorted_diff_keys,
)


def test_sort_keys_alphabetically_basic():
    env = {"ZEBRA": "1", "APPLE": "2", "MANGO": "3"}
    result = sort_keys_alphabetically(env)
    assert list(result.keys()) == ["APPLE", "MANGO", "ZEBRA"]


def test_sort_keys_alphabetically_empty():
    assert sort_keys_alphabetically({}) == {}


def test_sort_keys_alphabetically_preserves_values():
    env = {"B": "beta", "A": "alpha"}
    result = sort_keys_alphabetically(env)
    assert result["A"] == "alpha"
    assert result["B"] == "beta"


def test_group_keys_by_prefix_basic():
    env = {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_NAME": "envdiff",
        "DEBUG": "true",
    }
    groups = group_keys_by_prefix(env)
    assert set(groups["DB"].keys()) == {"DB_HOST", "DB_PORT"}
    assert groups["APP"] == {"APP_NAME": "envdiff"}
    assert groups[""] == {"DEBUG": "true"}


def test_group_keys_by_prefix_no_separator():
    env = {"NODASH": "value", "ALSO": "here"}
    groups = group_keys_by_prefix(env)
    assert "" in groups
    assert set(groups[""].keys()) == {"NODASH", "ALSO"}


def test_group_keys_by_prefix_custom_separator():
    env = {"NS.KEY": "val", "NS.OTHER": "val2", "PLAIN": "x"}
    groups = group_keys_by_prefix(env, separator=".")
    assert set(groups["NS"].keys()) == {"NS.KEY", "NS.OTHER"}
    assert groups[""] == {"PLAIN": "x"}


def test_group_keys_by_prefix_empty():
    assert group_keys_by_prefix({}) == {}


def test_sorted_diff_keys_disjoint():
    left = {"A": "1", "B": "2"}
    right = {"C": "3", "D": "4"}
    only_left, only_right, in_both = sorted_diff_keys(left, right)
    assert only_left == ["A", "B"]
    assert only_right == ["C", "D"]
    assert in_both == []


def test_sorted_diff_keys_overlap():
    left = {"A": "1", "B": "2", "C": "3"}
    right = {"B": "2", "C": "x", "D": "4"}
    only_left, only_right, in_both = sorted_diff_keys(left, right)
    assert only_left == ["A"]
    assert only_right == ["D"]
    assert in_both == ["B", "C"]


def test_sorted_diff_keys_identical():
    env = {"X": "1", "Y": "2"}
    only_left, only_right, in_both = sorted_diff_keys(env, env.copy())
    assert only_left == []
    assert only_right == []
    assert in_both == ["X", "Y"]


def test_sorted_diff_keys_both_empty():
    only_left, only_right, in_both = sorted_diff_keys({}, {})
    assert only_left == []
    assert only_right == []
    assert in_both == []
