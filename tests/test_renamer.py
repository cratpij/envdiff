"""Tests for envdiff.renamer."""

from __future__ import annotations

import pytest

from envdiff.renamer import RenameResult, rename_keys, rename_keys_in_file


# ---------------------------------------------------------------------------
# RenameResult helpers
# ---------------------------------------------------------------------------

def test_summary_no_renames():
    r = RenameResult()
    assert r.summary() == "No renames applied."


def test_summary_renamed_only():
    r = RenameResult(renamed={"OLD": "NEW"})
    assert "1 key(s) renamed" in r.summary()


def test_summary_skipped_only():
    r = RenameResult(skipped=["MISSING"])
    assert "1 key(s) not found (skipped)" in r.summary()


def test_summary_both():
    r = RenameResult(renamed={"A": "B"}, skipped=["C"])
    summary = r.summary()
    assert "1 key(s) renamed" in summary
    assert "1 key(s) not found (skipped)" in summary


# ---------------------------------------------------------------------------
# rename_keys
# ---------------------------------------------------------------------------

def test_basic_rename():
    env = {"OLD_KEY": "value", "OTHER": "x"}
    result = rename_keys(env, {"OLD_KEY": "NEW_KEY"})
    assert "NEW_KEY" in result.env
    assert "OLD_KEY" not in result.env
    assert result.env["NEW_KEY"] == "value"
    assert result.renamed == {"OLD_KEY": "NEW_KEY"}
    assert result.skipped == []


def test_missing_key_is_skipped():
    env = {"A": "1"}
    result = rename_keys(env, {"MISSING": "NEW"})
    assert "MISSING" not in result.env
    assert "NEW" not in result.env
    assert result.skipped == ["MISSING"]
    assert result.renamed == {}


def test_no_overwrite_by_default():
    env = {"OLD": "old_val", "NEW": "existing"}
    result = rename_keys(env, {"OLD": "NEW"})
    # Rename skipped because NEW already exists
    assert result.env["NEW"] == "existing"
    assert "OLD" in result.env
    assert "OLD" in result.skipped


def test_overwrite_flag():
    env = {"OLD": "fresh", "NEW": "stale"}
    result = rename_keys(env, {"OLD": "NEW"}, overwrite=True)
    assert result.env["NEW"] == "fresh"
    assert "OLD" not in result.env
    assert result.renamed == {"OLD": "NEW"}


def test_multiple_renames():
    env = {"A": "1", "B": "2", "C": "3"}
    result = rename_keys(env, {"A": "X", "B": "Y"})
    assert result.env == {"X": "1", "Y": "2", "C": "3"}
    assert set(result.renamed.keys()) == {"A", "B"}


def test_original_env_not_mutated():
    env = {"KEY": "val"}
    rename_keys(env, {"KEY": "NEW_KEY"})
    assert "KEY" in env  # original unchanged


# ---------------------------------------------------------------------------
# rename_keys_in_file
# ---------------------------------------------------------------------------

def test_rename_keys_in_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("DB_HOST=localhost\nDB_PORT=5432\n", encoding="utf-8")

    result = rename_keys_in_file(
        str(env_file),
        {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"},
    )

    assert result.env["DATABASE_HOST"] == "localhost"
    assert result.env["DATABASE_PORT"] == "5432"
    assert result.skipped == []


def test_rename_keys_in_file_missing_key(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("EXISTING=yes\n", encoding="utf-8")

    result = rename_keys_in_file(str(env_file), {"GHOST": "PHANTOM"})
    assert "GHOST" in result.skipped
    assert result.env == {"EXISTING": "yes"}
