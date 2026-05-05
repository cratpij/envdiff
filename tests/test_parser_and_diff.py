"""Tests for the parser and diff modules."""

import pytest
from pathlib import Path

from envdiff.parser import parse_env_file, _strip_quotes
from envdiff.diff import diff_envs, EnvDiffResult


# ---------------------------------------------------------------------------
# Parser tests
# ---------------------------------------------------------------------------

def test_parse_basic_env(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("DB_HOST=localhost\nDB_PORT=5432\n")
    result = parse_env_file(env_file)
    assert result == {"DB_HOST": "localhost", "DB_PORT": "5432"}


def test_parse_skips_comments_and_blank_lines(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("# comment\n\nKEY=value\n")
    result = parse_env_file(env_file)
    assert result == {"KEY": "value"}


def test_parse_strips_quoted_values(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text('SECRET="my secret"\nTOKEN=\'abc123\'\n')
    result = parse_env_file(env_file)
    assert result["SECRET"] == "my secret"
    assert result["TOKEN"] == "abc123"


def test_parse_file_not_found():
    with pytest.raises(FileNotFoundError):
        parse_env_file("/nonexistent/.env")


def test_parse_malformed_line(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("VALID=ok\nBAD LINE\n")
    with pytest.raises(ValueError, match="Malformed line"):
        parse_env_file(env_file)


def test_strip_quotes_no_quotes():
    assert _strip_quotes("hello") == "hello"


def test_strip_quotes_double():
    assert _strip_quotes('"hello"') == "hello"


def test_strip_quotes_single():
    assert _strip_quotes("'hello'") == "hello"


# ---------------------------------------------------------------------------
# Diff tests
# ---------------------------------------------------------------------------

def test_diff_no_differences():
    base = {"A": "1", "B": "2"}
    result = diff_envs(base, base.copy())
    assert not result.has_differences


def test_diff_missing_in_compare():
    base = {"A": "1", "B": "2"}
    compare = {"A": "1"}
    result = diff_envs(base, compare)
    assert "B" in result.missing_in_compare
    assert result.has_differences


def test_diff_missing_in_base():
    base = {"A": "1"}
    compare = {"A": "1", "C": "3"}
    result = diff_envs(base, compare)
    assert "C" in result.missing_in_base


def test_diff_mismatched_values():
    base = {"A": "1", "B": "old"}
    compare = {"A": "1", "B": "new"}
    result = diff_envs(base, compare, base_name="prod", compare_name="staging")
    assert "B" in result.mismatched
    assert result.mismatched["B"] == ("old", "new")


def test_diff_summary_contains_labels():
    result = diff_envs({"X": "1"}, {}, base_name="production", compare_name="local")
    summary = result.summary()
    assert "production" in summary
    assert "local" in summary
    assert "X" in summary
