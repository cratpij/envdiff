"""Tests for envdiff.scoper."""
import pytest

from envdiff.scoper import (
    Scope,
    ScopeResult,
    scope_diff,
    scope_diff_files,
)
from envdiff.diff import EnvDiffResult


# ---------------------------------------------------------------------------
# Scope.matches
# ---------------------------------------------------------------------------

def test_scope_matches_exact():
    s = Scope(name="db", patterns=["DB_HOST", "DB_PORT"])
    assert s.matches("DB_HOST")
    assert not s.matches("API_KEY")


def test_scope_matches_glob():
    s = Scope(name="db", patterns=["DB_*"])
    assert s.matches("DB_HOST")
    assert s.matches("DB_PORT")
    assert not s.matches("API_KEY")


def test_scope_matches_multiple_patterns():
    s = Scope(name="mixed", patterns=["DB_*", "API_KEY"])
    assert s.matches("DB_HOST")
    assert s.matches("API_KEY")
    assert not s.matches("SECRET")


def test_scope_matches_empty_patterns():
    s = Scope(name="empty", patterns=[])
    assert not s.matches("ANYTHING")


# ---------------------------------------------------------------------------
# scope_diff — basic behaviour
# ---------------------------------------------------------------------------

def _left():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "API_KEY": "abc"}


def _right():
    return {"DB_HOST": "prod.db", "DB_PORT": "5432", "SECRET": "xyz"}


def test_scope_diff_excludes_out_of_scope_keys():
    scope = Scope(name="db", patterns=["DB_*"])
    result = scope_diff(_left(), _right(), scope)
    assert "API_KEY" in result.excluded_keys
    assert "SECRET" in result.excluded_keys


def test_scope_diff_detects_mismatch_within_scope():
    scope = Scope(name="db", patterns=["DB_*"])
    result = scope_diff(_left(), _right(), scope)
    assert "DB_HOST" in result.diff.mismatched


def test_scope_diff_no_mismatch_for_equal_key():
    scope = Scope(name="db", patterns=["DB_*"])
    result = scope_diff(_left(), _right(), scope)
    assert "DB_PORT" not in result.diff.mismatched


def test_scope_diff_is_clean_when_no_differences():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    scope = Scope(name="db", patterns=["DB_*"])
    result = scope_diff(env, env.copy(), scope)
    assert result.is_clean


def test_scope_diff_not_clean_when_mismatch():
    scope = Scope(name="db", patterns=["DB_*"])
    result = scope_diff(_left(), _right(), scope)
    assert not result.is_clean


# ---------------------------------------------------------------------------
# ScopeResult.summary
# ---------------------------------------------------------------------------

def test_summary_clean():
    env = {"DB_HOST": "localhost"}
    scope = Scope(name="db", patterns=["DB_*"])
    result = scope_diff(env, env.copy(), scope)
    assert "No differences" in result.summary()


def test_summary_shows_mismatched():
    scope = Scope(name="db", patterns=["DB_*"])
    result = scope_diff(_left(), _right(), scope)
    assert "DB_HOST" in result.summary()


def test_summary_shows_excluded_count():
    scope = Scope(name="db", patterns=["DB_*"])
    result = scope_diff(_left(), _right(), scope)
    assert "Excluded keys" in result.summary()


# ---------------------------------------------------------------------------
# scope_diff_files
# ---------------------------------------------------------------------------

def test_scope_diff_files(tmp_path):
    left_file = tmp_path / ".env.left"
    right_file = tmp_path / ".env.right"
    left_file.write_text("DB_HOST=localhost\nAPI_KEY=abc\n")
    right_file.write_text("DB_HOST=prod.db\nAPI_KEY=abc\n")

    scope = Scope(name="db", patterns=["DB_*"])
    result = scope_diff_files(str(left_file), str(right_file), scope)
    assert "DB_HOST" in result.diff.mismatched
    assert "API_KEY" in result.excluded_keys
