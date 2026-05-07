"""Tests for envdiff.filter."""

import pytest

from envdiff.diff import EnvDiffResult
from envdiff.filter import (
    FilterOptions,
    filter_diff,
    filter_by_pattern,
    filter_by_prefix,
)


def _result() -> EnvDiffResult:
    return EnvDiffResult(
        missing_in_left={"DB_HOST": "localhost", "APP_SECRET": "abc"},
        missing_in_right={"REDIS_URL": "redis://localhost"},
        mismatched_values={
            "APP_ENV": ("development", "production"),
            "DB_PORT": ("5432", "5433"),
        },
    )


# ---------------------------------------------------------------------------
# filter_by_prefix
# ---------------------------------------------------------------------------

def test_filter_by_prefix_keeps_matching_keys():
    filtered = filter_by_prefix(_result(), "DB_")
    assert "DB_HOST" in filtered.missing_in_left
    assert "DB_PORT" in filtered.mismatched_values


def test_filter_by_prefix_removes_non_matching_keys():
    filtered = filter_by_prefix(_result(), "DB_")
    assert "APP_SECRET" not in filtered.missing_in_left
    assert "REDIS_URL" not in filtered.missing_in_right
    assert "APP_ENV" not in filtered.mismatched_values


def test_filter_by_prefix_empty_result_when_no_match():
    filtered = filter_by_prefix(_result(), "NONEXISTENT_")
    assert filtered.missing_in_left == {}
    assert filtered.missing_in_right == {}
    assert filtered.mismatched_values == {}


# ---------------------------------------------------------------------------
# filter_by_pattern
# ---------------------------------------------------------------------------

def test_filter_by_pattern_glob_star():
    filtered = filter_by_pattern(_result(), "APP_*")
    assert "APP_SECRET" in filtered.missing_in_left
    assert "APP_ENV" in filtered.mismatched_values
    assert "DB_HOST" not in filtered.missing_in_left


def test_filter_by_pattern_exact_key():
    filtered = filter_by_pattern(_result(), "REDIS_URL")
    assert filtered.missing_in_right == {"REDIS_URL": "redis://localhost"}
    assert filtered.missing_in_left == {}
    assert filtered.mismatched_values == {}


def test_filter_by_pattern_no_match_returns_empty():
    filtered = filter_by_pattern(_result(), "UNKNOWN_*")
    assert not filtered.missing_in_left
    assert not filtered.missing_in_right
    assert not filtered.mismatched_values


# ---------------------------------------------------------------------------
# filter_diff with FilterOptions change-type flags
# ---------------------------------------------------------------------------

def test_filter_options_exclude_missing_left():
    opts = FilterOptions(include_missing_left=False)
    filtered = filter_diff(_result(), opts)
    assert filtered.missing_in_left == {}
    assert filtered.missing_in_right  # still present


def test_filter_options_exclude_missing_right():
    opts = FilterOptions(include_missing_right=False)
    filtered = filter_diff(_result(), opts)
    assert filtered.missing_in_right == {}
    assert filtered.missing_in_left  # still present


def test_filter_options_exclude_mismatched():
    opts = FilterOptions(include_mismatched=False)
    filtered = filter_diff(_result(), opts)
    assert filtered.mismatched_values == {}
    assert filtered.missing_in_left  # still present


def test_filter_options_prefix_and_pattern_combined():
    # prefix DB_ AND pattern *_PORT — only DB_PORT should survive
    opts = FilterOptions(prefix="DB_", pattern="*_PORT")
    filtered = filter_diff(_result(), opts)
    assert "DB_PORT" in filtered.mismatched_values
    assert "DB_HOST" not in filtered.missing_in_left


def test_filter_diff_preserves_values():
    filtered = filter_by_prefix(_result(), "APP_")
    assert filtered.mismatched_values["APP_ENV"] == ("development", "production")
    assert filtered.missing_in_left["APP_SECRET"] == "abc"
