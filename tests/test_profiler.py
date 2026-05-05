"""Tests for envdiff.profiler."""

import os
import tempfile

import pytest

from envdiff.profiler import (
    EnvProfile,
    profile_env,
    profile_env_file,
    profile_raw_lines,
    LONG_VALUE_THRESHOLD,
)


def test_profile_env_empty():
    result = profile_env({})
    assert result.total_keys == 0
    assert result.avg_value_length == 0.0
    assert result.max_value_length == 0
    assert result.has_issues() is False


def test_profile_env_basic():
    env = {"A": "hello", "B": "world"}
    result = profile_env(env)
    assert result.total_keys == 2
    assert result.avg_value_length == 5.0
    assert result.max_value_length == 5
    assert result.has_issues() is False


def test_profile_env_empty_values():
    env = {"A": "", "B": "value"}
    result = profile_env(env)
    assert "A" in result.empty_values
    assert result.has_issues() is True


def test_profile_env_long_values():
    long_val = "x" * (LONG_VALUE_THRESHOLD + 1)
    env = {"SECRET": long_val, "SHORT": "hi"}
    result = profile_env(env)
    assert "SECRET" in result.long_values
    assert "SHORT" not in result.long_values


def test_profile_env_max_value_key():
    env = {"A": "short", "B": "much_longer_value"}
    result = profile_env(env)
    assert result.max_value_key == "B"
    assert result.max_value_length == len("much_longer_value")


def test_profile_env_path_stored():
    result = profile_env({"K": "v"}, path="/some/path/.env")
    assert result.path == "/some/path/.env"


def test_profile_env_file_reads_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("FOO=bar\nBAZ=qux\n")
        path = f.name
    try:
        result = profile_env_file(path)
        assert result.total_keys == 2
        assert result.path == path
    finally:
        os.unlink(path)


def test_profile_env_file_not_found():
    with pytest.raises(FileNotFoundError):
        profile_env_file("/nonexistent/.env")


def test_profile_raw_lines_no_duplicates():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("A=1\nB=2\nC=3\n")
        path = f.name
    try:
        dups = profile_raw_lines(path)
        assert dups == []
    finally:
        os.unlink(path)


def test_profile_raw_lines_with_duplicates():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("A=1\nB=2\nA=overridden\n")
        path = f.name
    try:
        dups = profile_raw_lines(path)
        assert "A" in dups
    finally:
        os.unlink(path)


def test_profile_raw_lines_skips_comments_and_blanks():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("# comment\n\nA=1\n")
        path = f.name
    try:
        dups = profile_raw_lines(path)
        assert dups == []
    finally:
        os.unlink(path)


def test_summary_contains_path():
    result = profile_env({"X": "y"}, path="test.env")
    s = result.summary()
    assert "test.env" in s
    assert "Total keys" in s
