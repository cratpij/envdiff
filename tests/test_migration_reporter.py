"""Tests for envdiff.migration_reporter."""
from envdiff.migrator import MigrationResult
from envdiff.migration_reporter import format_migration_report, print_migration_report


def _result(**kwargs) -> MigrationResult:
    defaults = dict(
        source_path="dev.env",
        target_path="prod.env",
        migrated={"DATABASE_HOST": "localhost", "DATABASE_PORT": "5432"},
        skipped=["OLD_SECRET"],
        warnings=[],
    )
    defaults.update(kwargs)
    return MigrationResult(**defaults)


def test_format_includes_header():
    report = format_migration_report(_result(), color=False)
    assert "Migration Report" in report
    assert "dev.env" in report


def test_format_uses_filename_override():
    report = format_migration_report(_result(), filename="custom.env", color=False)
    assert "custom.env" in report


def test_format_shows_target_path():
    report = format_migration_report(_result(), color=False)
    assert "prod.env" in report


def test_format_shows_migrated_keys():
    report = format_migration_report(_result(), color=False)
    assert "DATABASE_HOST" in report
    assert "localhost" in report


def test_format_shows_skipped_keys():
    report = format_migration_report(_result(), color=False)
    assert "OLD_SECRET" in report


def test_format_shows_warnings():
    r = _result(warnings=["Transform for 'X' failed: oops"])
    report = format_migration_report(r, color=False)
    assert "oops" in report
    assert "Warnings" in report


def test_format_no_keys_message():
    r = MigrationResult(source_path="a", target_path="b")
    report = format_migration_report(r, color=False)
    assert "No keys to migrate" in report


def test_print_migration_report_runs(capsys):
    print_migration_report(_result(), color=False)
    captured = capsys.readouterr()
    assert "Migration Report" in captured.out
