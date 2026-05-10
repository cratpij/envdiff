"""Tests for envdiff.archiver."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from envdiff.archiver import (
    ArchiveEntry,
    ArchiveResult,
    archive_envs,
    restore_archive,
)


# ---------------------------------------------------------------------------
# ArchiveResult helpers
# ---------------------------------------------------------------------------

def test_archive_result_entry_names():
    entries = [
        ArchiveEntry(path=".env.dev", env={}, captured_at=""),
        ArchiveEntry(path=".env.prod", env={}, captured_at=""),
    ]
    result = ArchiveResult(entries=entries)
    assert result.entry_names() == [".env.dev", ".env.prod"]


def test_archive_result_summary(tmp_path):
    archive_file = str(tmp_path / "out.zip")
    entries = [ArchiveEntry(path=".env", env={}, captured_at="")]
    result = ArchiveResult(entries=entries, archive_path=archive_file)
    assert "1 env file(s) archived" in result.summary()
    assert archive_file in result.summary()


# ---------------------------------------------------------------------------
# archive_envs
# ---------------------------------------------------------------------------

def test_archive_envs_creates_zip(tmp_path):
    archive_file = str(tmp_path / "archive.zip")
    env_map = {".env.dev": {"KEY": "value"}}
    result = archive_envs(env_map, archive_file)
    assert Path(archive_file).exists()
    assert result.archive_path == archive_file


def test_archive_envs_entry_count(tmp_path):
    archive_file = str(tmp_path / "archive.zip")
    env_map = {
        ".env.dev": {"A": "1"},
        ".env.prod": {"A": "2", "B": "3"},
    }
    result = archive_envs(env_map, archive_file)
    assert len(result.entries) == 2


def test_archive_envs_zip_contains_json_files(tmp_path):
    archive_file = str(tmp_path / "archive.zip")
    env_map = {".env.staging": {"X": "y"}}
    archive_envs(env_map, archive_file)
    with zipfile.ZipFile(archive_file) as zf:
        names = zf.namelist()
    assert any(name.endswith(".json") for name in names)


def test_archive_envs_captured_at_is_set(tmp_path):
    archive_file = str(tmp_path / "archive.zip")
    result = archive_envs({".env": {"FOO": "bar"}}, archive_file)
    assert result.entries[0].captured_at != ""


# ---------------------------------------------------------------------------
# restore_archive
# ---------------------------------------------------------------------------

def test_restore_archive_returns_same_paths(tmp_path):
    archive_file = str(tmp_path / "archive.zip")
    env_map = {".env.dev": {"A": "1"}, ".env.prod": {"B": "2"}}
    archive_envs(env_map, archive_file)
    result = restore_archive(archive_file)
    assert set(result.entry_names()) == set(env_map.keys())


def test_restore_archive_preserves_values(tmp_path):
    archive_file = str(tmp_path / "archive.zip")
    env_map = {".env": {"SECRET": "abc123", "PORT": "8080"}}
    archive_envs(env_map, archive_file)
    result = restore_archive(archive_file)
    assert result.entries[0].env == {"SECRET": "abc123", "PORT": "8080"}


def test_restore_archive_sets_archive_path(tmp_path):
    archive_file = str(tmp_path / "archive.zip")
    archive_envs({".env": {}}, archive_file)
    result = restore_archive(archive_file)
    assert result.archive_path == archive_file


def test_restore_empty_env(tmp_path):
    archive_file = str(tmp_path / "archive.zip")
    archive_envs({".env": {}}, archive_file)
    result = restore_archive(archive_file)
    assert result.entries[0].env == {}
