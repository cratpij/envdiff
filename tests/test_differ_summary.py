"""Tests for differ_summary and summary_reporter."""

import pytest

from envdiff.diff import EnvDiffResult
from envdiff.differ_summary import DiffSummaryStats, compute_summary
from envdiff.summary_reporter import format_summary_report


def _result(
    missing_in_right=None,
    missing_in_left=None,
    mismatched=None,
) -> EnvDiffResult:
    return EnvDiffResult(
        missing_in_right=missing_in_right or [],
        missing_in_left=missing_in_left or [],
        mismatched=mismatched or {},
    )


# --- DiffSummaryStats unit tests ---

def test_stats_defaults():
    s = DiffSummaryStats()
    assert s.total_issues == 0
    assert s.is_clean is True


def test_stats_total_issues():
    s = DiffSummaryStats(
        total_missing_in_right=2,
        total_missing_in_left=1,
        total_mismatched=3,
    )
    assert s.total_issues == 6
    assert s.is_clean is False


def test_stats_summary_clean():
    s = DiffSummaryStats(total_files=3)
    assert "identical" in s.summary()
    assert "3" in s.summary()


def test_stats_summary_with_issues():
    s = DiffSummaryStats(
        total_files=4,
        files_with_differences=2,
        total_missing_in_right=1,
        total_missing_in_left=2,
        total_mismatched=3,
    )
    msg = s.summary()
    assert "2/4" in msg
    assert "missing-right" in msg


# --- compute_summary tests ---

def test_compute_summary_empty():
    stats = compute_summary([])
    assert stats.total_files == 0
    assert stats.is_clean is True


def test_compute_summary_no_differences():
    results = [
        ("prod vs staging", _result()),
        ("prod vs dev", _result()),
    ]
    stats = compute_summary(results)
    assert stats.total_files == 2
    assert stats.files_with_differences == 0
    assert stats.is_clean is True


def test_compute_summary_with_differences():
    results = [
        ("A vs B", _result(missing_in_right=["FOO"], mismatched={"BAR": ("1", "2")})),
        ("A vs C", _result()),
    ]
    stats = compute_summary(results)
    assert stats.total_files == 2
    assert stats.files_with_differences == 1
    assert stats.total_missing_in_right == 1
    assert stats.total_mismatched == 1
    assert stats.total_missing_in_left == 0


def test_compute_summary_per_file_keys():
    results = [("x vs y", _result(missing_in_left=["A", "B"]))]
    stats = compute_summary(results)
    assert "x vs y" in stats.per_file
    assert stats.per_file["x vs y"]["missing_in_left"] == 2


# --- format_summary_report tests ---

def test_format_report_clean(capsys):
    stats = compute_summary([("a vs b", _result())])
    report = format_summary_report(stats, colour=False)
    assert "Diff Summary" in report
    assert "identical" in report


def test_format_report_shows_per_file_label():
    results = [("prod vs dev", _result(missing_in_right=["SECRET"]))]
    stats = compute_summary(results)
    report = format_summary_report(stats, colour=False)
    assert "prod vs dev" in report
    assert "miss-r=1" in report


def test_format_report_colour_disabled_no_escape():
    stats = compute_summary([("a vs b", _result())])
    report = format_summary_report(stats, colour=False)
    assert "\033[" not in report
