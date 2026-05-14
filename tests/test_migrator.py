"""Tests for envdiff.migrator."""
import pytest

from envdiff.migrator import MigrationResult, migrate_envs, migrate_env_files


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _source() -> dict:
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "s3cr3t"}


# ---------------------------------------------------------------------------
# MigrationResult
# ---------------------------------------------------------------------------

def test_migration_result_defaults():
    r = MigrationResult(source_path="a", target_path="b")
    assert r.migrated == {}
    assert r.skipped == []
    assert r.warnings == []
    assert not r.has_warnings


def test_migration_result_summary_basic():
    r = MigrationResult(source_path="a.env", target_path="b.env",
                        migrated={"NEW_HOST": "localhost"}, skipped=["MISSING"])
    s = r.summary()
    assert "a.env" in s
    assert "b.env" in s
    assert "1 key(s)" in s  # migrated
    assert "1 key(s)" in s  # skipped


def test_migration_result_summary_warnings():
    r = MigrationResult(source_path="a", target_path="b",
                        warnings=["Transform for 'X' failed: oops"])
    assert "WARNING" in r.summary()
    assert r.has_warnings


# ---------------------------------------------------------------------------
# migrate_envs
# ---------------------------------------------------------------------------

def test_migrate_envs_basic_rename():
    result = migrate_envs(
        _source(),
        {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"},
    )
    assert result.migrated["DATABASE_HOST"] == "localhost"
    assert result.migrated["DATABASE_PORT"] == "5432"
    assert result.skipped == []


def test_migrate_envs_missing_key_goes_to_skipped():
    result = migrate_envs(_source(), {"NONEXISTENT": "NEW_KEY"})
    assert "NONEXISTENT" in result.skipped
    assert "NEW_KEY" not in result.migrated


def test_migrate_envs_with_transform():
    result = migrate_envs(
        _source(),
        {"DB_PORT": "DATABASE_PORT"},
        transforms={"DB_PORT": lambda k, v: str(int(v) + 1)},
    )
    assert result.migrated["DATABASE_PORT"] == "5433"


def test_migrate_envs_transform_error_produces_warning():
    def bad_transform(k, v):
        raise ValueError("boom")

    result = migrate_envs(
        _source(),
        {"DB_PORT": "DATABASE_PORT"},
        transforms={"DB_PORT": bad_transform},
    )
    assert result.has_warnings
    assert any("boom" in w for w in result.warnings)
    # value should still be the original (pre-transform)
    assert result.migrated["DATABASE_PORT"] == "5432"


def test_migrate_envs_duplicate_target_warns():
    result = migrate_envs(
        {"A": "1", "B": "2"},
        {"A": "SAME", "B": "SAME"},
    )
    assert result.has_warnings
    assert any("SAME" in w for w in result.warnings)


def test_migrate_envs_empty_rename_map():
    result = migrate_envs(_source(), {})
    assert result.migrated == {}
    assert result.skipped == []


# ---------------------------------------------------------------------------
# migrate_env_files
# ---------------------------------------------------------------------------

def test_migrate_env_files(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("DB_HOST=localhost\nDB_PORT=5432\n")
    result = migrate_env_files(
        str(env_file),
        {"DB_HOST": "DATABASE_HOST"},
        target_path="prod.env",
    )
    assert result.migrated["DATABASE_HOST"] == "localhost"
    assert result.source_path == str(env_file)
    assert result.target_path == "prod.env"
