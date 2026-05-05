"""Tests for envdiff.merger."""

import pytest
from unittest.mock import patch

from envdiff.merger import merge_envs, merge_env_files, MergeConflict


# ---------------------------------------------------------------------------
# merge_envs
# ---------------------------------------------------------------------------

def test_merge_envs_no_overlap():
    a = {"A": "1", "B": "2"}
    b = {"C": "3"}
    result = merge_envs([a, b])
    assert result == {"A": "1", "B": "2", "C": "3"}


def test_merge_envs_strategy_last():
    a = {"KEY": "old"}
    b = {"KEY": "new"}
    result = merge_envs([a, b], strategy="last")
    assert result["KEY"] == "new"


def test_merge_envs_strategy_first():
    a = {"KEY": "old"}
    b = {"KEY": "new"}
    result = merge_envs([a, b], strategy="first")
    assert result["KEY"] == "old"


def test_merge_envs_strategy_error_no_conflict():
    a = {"A": "1"}
    b = {"B": "2"}
    result = merge_envs([a, b], strategy="error")
    assert result == {"A": "1", "B": "2"}


def test_merge_envs_strategy_error_same_value_no_raise():
    """Same key with identical value should not raise even with 'error' strategy."""
    a = {"KEY": "same"}
    b = {"KEY": "same"}
    result = merge_envs([a, b], strategy="error")
    assert result["KEY"] == "same"


def test_merge_envs_strategy_error_raises_on_conflict():
    a = {"KEY": "alpha"}
    b = {"KEY": "beta"}
    with pytest.raises(MergeConflict) as exc_info:
        merge_envs([a, b], sources=["file_a", "file_b"], strategy="error")
    err = exc_info.value
    assert err.key == "KEY"
    assert "file_a" in err.values
    assert "file_b" in err.values
    assert "KEY" in str(err)


def test_merge_envs_empty_list():
    result = merge_envs([])
    assert result == {}


def test_merge_envs_single_map():
    a = {"X": "10"}
    result = merge_envs([a])
    assert result == {"X": "10"}


def test_merge_envs_default_source_labels():
    """When sources is None, integer labels are used internally without error."""
    a = {"K": "v1"}
    b = {"K": "v2"}
    with pytest.raises(MergeConflict) as exc_info:
        merge_envs([a, b], strategy="error")
    assert exc_info.value.key == "K"


# ---------------------------------------------------------------------------
# merge_env_files
# ---------------------------------------------------------------------------

def test_merge_env_files_calls_parse_and_merges():
    parsed = [{"DB": "postgres"}, {"PORT": "5432"}]
    with patch("envdiff.merger.parse_env_file", side_effect=parsed) as mock_parse:
        result = merge_env_files([".env.base", ".env.local"])
    assert mock_parse.call_count == 2
    assert result == {"DB": "postgres", "PORT": "5432"}


def test_merge_env_files_strategy_propagated():
    parsed = [{"K": "a"}, {"K": "b"}]
    with patch("envdiff.merger.parse_env_file", side_effect=parsed):
        with pytest.raises(MergeConflict):
            merge_env_files([".env.a", ".env.b"], strategy="error")
