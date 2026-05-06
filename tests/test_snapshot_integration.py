"""Integration tests: capture → save → modify → diff → report."""

import io
import pytest

from envdiff.snapshotter import capture_snapshot, save_snapshot, diff_against_snapshot
from envdiff.snapshot_reporter import format_snapshot_report, print_snapshot_report


def _write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


@pytest.fixture()
def env_and_snap(tmp_path):
    env = _write(tmp_path, ".env", "DB_HOST=localhost\nDB_PORT=5432\nSECRET=abc\n")
    snap = capture_snapshot(env)
    snap_file = str(tmp_path / "snap.json")
    save_snapshot(snap, snap_file)
    return env, snap_file, tmp_path


def test_full_cycle_no_changes(env_and_snap):
    env, snap_file, _ = env_and_snap
    result, snap = diff_against_snapshot(env, snap_file)
    assert not result.has_differences()
    report = format_snapshot_report(result, snap)
    assert "No changes" in report


def test_full_cycle_added_key(env_and_snap, tmp_path):
    _, snap_file, tp = env_and_snap
    env2 = _write(tp, ".env", "DB_HOST=localhost\nDB_PORT=5432\nSECRET=abc\nNEW=val\n")
    result, snap = diff_against_snapshot(env2, snap_file)
    assert "NEW" in result.missing_in_left
    report = format_snapshot_report(result, snap)
    assert "NEW" in report


def test_full_cycle_removed_key(env_and_snap, tmp_path):
    _, snap_file, tp = env_and_snap
    env2 = _write(tp, ".env", "DB_HOST=localhost\nDB_PORT=5432\n")
    result, snap = diff_against_snapshot(env2, snap_file)
    assert "SECRET" in result.missing_in_right


def test_full_cycle_changed_value(env_and_snap, tmp_path):
    _, snap_file, tp = env_and_snap
    env2 = _write(tp, ".env", "DB_HOST=remotehost\nDB_PORT=5432\nSECRET=abc\n")
    result, snap = diff_against_snapshot(env2, snap_file)
    assert "DB_HOST" in result.mismatched
    old, new = result.mismatched["DB_HOST"]
    assert old == "localhost"
    assert new == "remotehost"


def test_print_report_integration(env_and_snap, tmp_path):
    _, snap_file, tp = env_and_snap
    env2 = _write(tp, ".env", "DB_HOST=changed\nDB_PORT=5432\nSECRET=abc\nEXTRA=yes\n")
    result, snap = diff_against_snapshot(env2, snap_file)
    buf = io.StringIO()
    print_snapshot_report(result, snap, file=buf)
    output = buf.getvalue()
    assert "DB_HOST" in output
    assert "EXTRA" in output
