"""Tests for envdiff.stripper."""

from __future__ import annotations

import pytest

from envdiff.stripper import StripResult, strip_keys, strip_env_file


_ENV = {
    "APP_HOST": "localhost",
    "APP_PORT": "8080",
    "DB_URL": "postgres://localhost/db",
    "SECRET_KEY": "abc123",
    "DEBUG": "true",
}


# ---------------------------------------------------------------------------
# StripResult helpers
# ---------------------------------------------------------------------------

def test_strip_result_total_removed():
    r = StripResult(original=_ENV, stripped={}, removed_keys=["A", "B"])
    assert r.total_removed() == 2


def test_strip_result_summary_no_removals():
    r = StripResult(original=_ENV, stripped=_ENV, removed_keys=[])
    assert r.summary() == "No keys removed."


def test_strip_result_summary_with_removals():
    r = StripResult(original=_ENV, stripped={}, removed_keys=["SECRET_KEY", "DEBUG"])
    assert "2 key(s)" in r.summary()
    assert "DEBUG" in r.summary()
    assert "SECRET_KEY" in r.summary()


# ---------------------------------------------------------------------------
# strip_keys — explicit key list
# ---------------------------------------------------------------------------

def test_strip_by_explicit_keys():
    result = strip_keys(_ENV, keys=["SECRET_KEY", "DEBUG"])
    assert "SECRET_KEY" not in result.stripped
    assert "DEBUG" not in result.stripped
    assert "APP_HOST" in result.stripped
    assert set(result.removed_keys) == {"SECRET_KEY", "DEBUG"}


def test_strip_by_explicit_keys_unknown_key_ignored():
    result = strip_keys(_ENV, keys=["NONEXISTENT"])
    assert result.removed_keys == []
    assert result.stripped == _ENV


# ---------------------------------------------------------------------------
# strip_keys — prefix
# ---------------------------------------------------------------------------

def test_strip_by_prefix():
    result = strip_keys(_ENV, prefix="APP_")
    assert "APP_HOST" not in result.stripped
    assert "APP_PORT" not in result.stripped
    assert "DB_URL" in result.stripped
    assert len(result.removed_keys) == 2


def test_strip_by_prefix_no_match():
    result = strip_keys(_ENV, prefix="XYZ_")
    assert result.removed_keys == []


# ---------------------------------------------------------------------------
# strip_keys — pattern
# ---------------------------------------------------------------------------

def test_strip_by_glob_pattern():
    result = strip_keys(_ENV, pattern="*SECRET*")
    assert "SECRET_KEY" not in result.stripped
    assert len(result.removed_keys) == 1


def test_strip_by_pattern_star_matches_all():
    result = strip_keys(_ENV, pattern="*")
    assert result.stripped == {}
    assert len(result.removed_keys) == len(_ENV)


# ---------------------------------------------------------------------------
# strip_keys — multiple selectors
# ---------------------------------------------------------------------------

def test_strip_combined_selectors():
    result = strip_keys(_ENV, prefix="DB_", keys=["DEBUG"])
    assert "DB_URL" not in result.stripped
    assert "DEBUG" not in result.stripped
    assert "APP_HOST" in result.stripped


# ---------------------------------------------------------------------------
# strip_keys — error when no selector given
# ---------------------------------------------------------------------------

def test_strip_no_selector_raises():
    with pytest.raises(ValueError, match="At least one"):
        strip_keys(_ENV)


# ---------------------------------------------------------------------------
# strip_env_file
# ---------------------------------------------------------------------------

def test_strip_env_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("APP_HOST=localhost\nSECRET_KEY=abc123\nDEBUG=true\n")
    result = strip_env_file(str(env_file), keys=["SECRET_KEY"])
    assert "SECRET_KEY" not in result.stripped
    assert "APP_HOST" in result.stripped
    assert result.total_removed() == 1


def test_strip_env_file_not_found():
    with pytest.raises(FileNotFoundError):
        strip_env_file("/no/such/file.env", prefix="X_")
