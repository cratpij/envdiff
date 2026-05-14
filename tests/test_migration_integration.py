"""Integration tests for the full migrate_env_files -> format_migration_report pipeline."""
import pytest

from envdiff.migrator import migrate_env_files
from envdiff.migration_reporter import format_migration_report


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env.dev"
    p.write_text(
        "DB_HOST=db.dev.internal\n"
        "DB_PORT=5432\n"
        "APP_SECRET=hunter2\n"
        "LEGACY_FLAG=true\n"
    )
    return str(p)


def test_integration_all_keys_migrated(env_file):
    rename_map = {
        "DB_HOST": "DATABASE_HOST",
        "DB_PORT": "DATABASE_PORT",
        "APP_SECRET": "APPLICATION_SECRET",
    }
    result = migrate_env_files(env_file, rename_map, target_path=".env.prod")
    assert set(result.migrated.keys()) == {"DATABASE_HOST", "DATABASE_PORT", "APPLICATION_SECRET"}
    assert result.skipped == []
    assert not result.has_warnings


def test_integration_missing_key_skipped(env_file):
    rename_map = {"DOES_NOT_EXIST": "NEW_KEY", "DB_HOST": "DATABASE_HOST"}
    result = migrate_env_files(env_file, rename_map)
    assert "DOES_NOT_EXIST" in result.skipped
    assert "DATABASE_HOST" in result.migrated


def test_integration_transform_applied(env_file):
    result = migrate_env_files(
        env_file,
        {"DB_PORT": "DATABASE_PORT"},
        transforms={"DB_PORT": lambda k, v: str(int(v) * 2)},
    )
    assert result.migrated["DATABASE_PORT"] == "10864"


def test_integration_report_contains_all_migrated_keys(env_file):
    rename_map = {"DB_HOST": "DATABASE_HOST", "LEGACY_FLAG": "FEATURE_FLAG"}
    result = migrate_env_files(env_file, rename_map)
    report = format_migration_report(result, color=False)
    assert "DATABASE_HOST" in report
    assert "FEATURE_FLAG" in report


def test_integration_report_shows_skipped(env_file):
    result = migrate_env_files(env_file, {"GHOST_KEY": "NEW_GHOST"})
    report = format_migration_report(result, color=False)
    assert "GHOST_KEY" in report
    assert "Skipped" in report
