"""Tests for envdiff.scheduler."""

from __future__ import annotations

import os
import tempfile
import pytest

from envdiff.scheduler import ScheduleEntry, ScheduleLog, run_once, run_schedule
from envdiff.diff import EnvDiffResult


def _write(path: str, content: str) -> None:
    with open(path, "w") as f:
        f.write(content)


@pytest.fixture()
def env_pair(tmp_path):
    left = str(tmp_path / ".env.left")
    right = str(tmp_path / ".env.right")
    _write(left, "FOO=bar\nBAZ=qux\n")
    _write(right, "FOO=bar\nBAZ=qux\n")
    return left, right


def test_schedule_log_empty_summary():
    log = ScheduleLog()
    assert "No scheduled runs" in log.summary()


def test_schedule_log_totals():
    log = ScheduleLog()
    clean = EnvDiffResult(set(), set(), {})
    dirty = EnvDiffResult({"X"}, set(), {})
    log.add(ScheduleEntry("2024-01-01T00:00:00Z", "a", "b", clean))
    log.add(ScheduleEntry("2024-01-01T00:01:00Z", "a", "b", dirty))
    assert log.total_runs == 2
    assert log.runs_with_differences == 1
    assert "Runs: 2" in log.summary()
    assert "With differences: 1" in log.summary()


def test_run_once_no_diff(env_pair):
    left, right = env_pair
    log = ScheduleLog()
    entry = run_once(left, right, log=log)
    assert not entry.result.has_differences
    assert log.total_runs == 1
    assert entry.left_path == left
    assert entry.right_path == right


def test_run_once_with_diff(tmp_path):
    left = str(tmp_path / "a.env")
    right = str(tmp_path / "b.env")
    _write(left, "FOO=bar\nEXTRA=only_left\n")
    _write(right, "FOO=bar\n")
    entry = run_once(left, right)
    assert entry.result.has_differences
    assert "EXTRA" in entry.result.missing_in_right


def test_run_once_calls_on_diff_callback(tmp_path):
    left = str(tmp_path / "a.env")
    right = str(tmp_path / "b.env")
    _write(left, "FOO=bar\n")
    _write(right, "FOO=changed\n")
    triggered = []
    run_once(left, right, on_diff=lambda e: triggered.append(e))
    assert len(triggered) == 1


def test_run_once_no_callback_on_clean(env_pair):
    left, right = env_pair
    triggered = []
    run_once(left, right, on_diff=lambda e: triggered.append(e))
    assert triggered == []


def test_run_schedule_max_runs(env_pair):
    left, right = env_pair
    log = run_schedule(left, right, interval_seconds=0, max_runs=3)
    assert log.total_runs == 3


def test_run_schedule_returns_log(env_pair):
    left, right = env_pair
    log = ScheduleLog()
    result = run_schedule(left, right, interval_seconds=0, max_runs=2, log=log)
    assert result is log
    assert log.total_runs == 2


def test_entry_timestamp_format(env_pair):
    left, right = env_pair
    entry = run_once(left, right)
    assert entry.timestamp.endswith("Z")
    assert "T" in entry.timestamp
