"""Tests for envdiff.normalizer."""

from __future__ import annotations

import pytest

from envdiff.normalizer import (
    diff_normalized,
    normalize_env,
    normalize_env_file,
    normalize_key,
    normalize_value,
)


# ---------------------------------------------------------------------------
# normalize_key
# ---------------------------------------------------------------------------

def test_normalize_key_uppercases():
    assert normalize_key("db_host") == "DB_HOST"


def test_normalize_key_strips_whitespace():
    assert normalize_key("  Port  ") == "PORT"


def test_normalize_key_already_upper():
    assert normalize_key("API_KEY") == "API_KEY"


# ---------------------------------------------------------------------------
# normalize_value
# ---------------------------------------------------------------------------

def test_normalize_value_strips():
    assert normalize_value("  hello  ") == "hello"


def test_normalize_value_empty():
    assert normalize_value("") == ""


def test_normalize_value_no_change():
    assert normalize_value("localhost") == "localhost"


# ---------------------------------------------------------------------------
# normalize_env
# ---------------------------------------------------------------------------

def test_normalize_env_uppercases_keys():
    result = normalize_env({"host": "localhost", "port": "5432"})
    assert "HOST" in result
    assert "PORT" in result


def test_normalize_env_strips_values():
    result = normalize_env({"KEY": "  value  "})
    assert result["KEY"] == "value"


def test_normalize_env_collision_last_wins():
    # Python dicts preserve insertion order; last normalized key wins
    result = normalize_env({"key": "first", "KEY": "second"})
    assert result["KEY"] == "second"


def test_normalize_env_empty():
    assert normalize_env({}) == {}


# ---------------------------------------------------------------------------
# normalize_env_file
# ---------------------------------------------------------------------------

def test_normalize_env_file_reads_and_normalizes(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("db_host=localhost\nDB_PORT=5432\n")
    result = normalize_env_file(str(env_file))
    assert result["DB_HOST"] == "localhost"
    assert result["DB_PORT"] == "5432"


def test_normalize_env_file_not_found():
    with pytest.raises(FileNotFoundError):
        normalize_env_file("/nonexistent/.env")


# ---------------------------------------------------------------------------
# diff_normalized
# ---------------------------------------------------------------------------

def test_diff_normalized_no_differences():
    env = {"A": "1", "B": "2"}
    result = diff_normalized(env, env.copy())
    assert result["missing_in_right"] == []
    assert result["missing_in_left"] == []
    assert result["mismatched"] == {}


def test_diff_normalized_missing_in_right():
    left = {"A": "1", "B": "2"}
    right = {"A": "1"}
    result = diff_normalized(left, right)
    assert result["missing_in_right"] == ["B"]
    assert result["missing_in_left"] == []


def test_diff_normalized_missing_in_left():
    left = {"A": "1"}
    right = {"A": "1", "C": "3"}
    result = diff_normalized(left, right)
    assert result["missing_in_left"] == ["C"]


def test_diff_normalized_mismatch():
    left = {"A": "old"}
    right = {"A": "new"}
    result = diff_normalized(left, right, left_name="dev", right_name="prod")
    assert "A" in result["mismatched"]
    assert result["mismatched"]["A"] == {"dev": "old", "prod": "new"}


def test_diff_normalized_sorted_output():
    left = {"Z": "1", "A": "1", "M": "1"}
    right = {}
    result = diff_normalized(left, right)
    assert result["missing_in_right"] == ["A", "M", "Z"]
