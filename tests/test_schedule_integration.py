"""Integration tests for scheduler + schedule_reporter."""

from __future__ import annotations

import pytest

from envdiff.scheduler import run_schedule, ScheduleLog
from envdiff.schedule_reporter import format_schedule_report


def _write(path: str, content: str) -> None:
    with open(path, "w") as f:
        f.write(content)


@pytest.fixture()
def identical_envs(tmp_path):
    left = str(tmp_path / "left.env")
    right = str(tmp_path / "right.env")
    _write(left, "A=1\nB=2\n")
    _write(right, "A=1\nB=2\n")
    return left, right


@pytest.fixture()
def diverged_envs(tmp_path):
    left = str(tmp_path / "left.env")
    right = str(tmp_path / "right.env")
    _write(left, "A=1\nB=2\nC=only_left\n")
    _write(right, "A=1\nB=different\n")
    return left, right


def test_identical_envs_all_clean(identical_envs):
    left, right = identical_envs
    log = run_schedule(left, right, interval_seconds=0, max_runs=4)
    assert log.runs_with_differences == 0
    assert log.total_runs == 4


def test_diverged_envs_all_dirty(diverged_envs):
    left, right = diverged_envs
    log = run_schedule(left, right, interval_seconds=0, max_runs=3)
    assert log.runs_with_differences == 3


def test_report_includes_all_runs(diverged_envs):
    left, right = diverged_envs
    log = run_schedule(left, right, interval_seconds=0, max_runs=2)
    report = format_schedule_report(log, use_color=False)
    assert report.count("DIFF") == 2


def test_report_summary_matches_log(identical_envs):
    left, right = identical_envs
    log = run_schedule(left, right, interval_seconds=0, max_runs=5)
    report = format_schedule_report(log, use_color=False)
    assert "Runs: 5" in report
    assert "Clean: 5" in report


def test_on_diff_callback_fires_for_each_dirty_run(diverged_envs):
    left, right = diverged_envs
    fired = []
    run_schedule(
        left, right,
        interval_seconds=0,
        max_runs=3,
        on_diff=lambda e: fired.append(e.timestamp),
    )
    assert len(fired) == 3
