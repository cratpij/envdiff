"""Tests for envdiff.snapshot_reporter."""

import io
from envdiff.snapshotter import Snapshot
from envdiff.diff import EnvDiffResult
from envdiff.snapshot_reporter import format_snapshot_report, print_snapshot_report


TS = "2024-06-01T12:00:00+00:00"
PATH = ".env.prod"


def _snap(**values):
    return Snapshot(path=PATH, captured_at=TS, values=values)


def _result(missing_left=None, missing_right=None, mismatched=None, common=None):
    return EnvDiffResult(
        missing_in_left=missing_left or set(),
        missing_in_right=missing_right or set(),
        mismatched=mismatched or {},
        common_keys=common or set(),
    )


def test_no_changes_message():
    report = format_snapshot_report(_result(), _snap())
    assert "No changes since snapshot" in report


def test_report_includes_timestamp():
    report = format_snapshot_report(_result(), _snap())
    assert TS in report


def test_report_includes_source_path():
    report = format_snapshot_report(_result(), _snap())
    assert PATH in report


def test_added_key_shown():
    result = _result(missing_left={"NEW_KEY"})
    report = format_snapshot_report(result, _snap())
    assert "NEW_KEY" in report
    assert "+" in report


def test_removed_key_shown():
    result = _result(missing_right={"OLD_KEY"})
    report = format_snapshot_report(result, _snap())
    assert "OLD_KEY" in report
    assert "-" in report


def test_changed_value_shown():
    result = _result(mismatched={"FOO": ("old_val", "new_val")})
    report = format_snapshot_report(result, _snap())
    assert "FOO" in report
    assert "old_val" in report
    assert "new_val" in report


def test_changed_value_labels():
    result = _result(mismatched={"BAR": ("snap_val", "cur_val")})
    report = format_snapshot_report(result, _snap())
    assert "snapshot" in report
    assert "current" in report


def test_print_snapshot_report_writes_to_file():
    result = _result(missing_left={"X"})
    buf = io.StringIO()
    print_snapshot_report(result, _snap(), file=buf)
    assert "X" in buf.getvalue()


def test_no_differences_no_change_sections():
    report = format_snapshot_report(_result(common={"A", "B"}), _snap(A="1", B="2"))
    assert "added" not in report.lower() or "No changes" in report
    assert "removed" not in report.lower() or "No changes" in report
