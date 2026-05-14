"""Tests for envdiff.schedule_reporter."""

from __future__ import annotations

import pytest

from envdiff.scheduler import ScheduleEntry, ScheduleLog
from envdiff.diff import EnvDiffResult
from envdiff.schedule_reporter import format_schedule_report, print_schedule_report


def _clean_entry() -> ScheduleEntry:
    return ScheduleEntry(
        timestamp="2024-06-01T10:00:00Z",
        left_path=".env.dev",
        right_path=".env.prod",
        result=EnvDiffResult(set(), set(), {}),
    )


def _diff_entry() -> ScheduleEntry:
    return ScheduleEntry(
        timestamp="2024-06-01T10:05:00Z",
        left_path=".env.dev",
        right_path=".env.prod",
        result=EnvDiffResult({"MISSING_KEY"}, set(), {"VAL": ("a", "b")}),
    )


def _log(*entries: ScheduleEntry) -> ScheduleLog:
    log = ScheduleLog()
    for e in entries:
        log.add(e)
    return log


def test_format_includes_header():
    report = format_schedule_report(_log(), use_color=False)
    assert "Schedule Report" in report


def test_format_uses_filename():
    report = format_schedule_report(_log(), filename="myfile", use_color=False)
    assert "myfile" in report


def test_format_empty_log():
    report = format_schedule_report(_log(), use_color=False)
    assert "No runs recorded" in report


def test_format_clean_entry_shows_ok():
    report = format_schedule_report(_log(_clean_entry()), use_color=False)
    assert "OK" in report
    assert "2024-06-01T10:00:00Z" in report


def test_format_diff_entry_shows_diff():
    report = format_schedule_report(_log(_diff_entry()), use_color=False)
    assert "DIFF" in report


def test_format_diff_shows_missing_in_right():
    report = format_schedule_report(_log(_diff_entry()), use_color=False)
    assert "MISSING_KEY" in report


def test_format_diff_shows_mismatched():
    report = format_schedule_report(_log(_diff_entry()), use_color=False)
    assert "VAL" in report


def test_format_summary_shown():
    log = _log(_clean_entry(), _diff_entry())
    report = format_schedule_report(log, use_color=False)
    assert "Runs: 2" in report
    assert "With differences: 1" in report


def test_print_schedule_report_runs(capsys):
    log = _log(_clean_entry())
    print_schedule_report(log, use_color=False)
    out = capsys.readouterr().out
    assert "Schedule Report" in out
