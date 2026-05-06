"""Tests for envdiff.grouper and envdiff.grouper_reporter."""

from __future__ import annotations

import io

import pytest

from envdiff.diff import EnvDiffResult
from envdiff.grouper import (
    GroupSummary,
    _extract_prefix,
    group_diff_by_prefix,
    top_problem_groups,
)
from envdiff.grouper_reporter import format_group_report, print_group_report


def _result(
    missing_right=(),
    missing_left=(),
    mismatched=None,
) -> EnvDiffResult:
    return EnvDiffResult(
        missing_in_right=list(missing_right),
        missing_in_left=list(missing_left),
        mismatched_values=dict(mismatched or {}),
    )


# --- _extract_prefix ---

def test_extract_prefix_basic():
    assert _extract_prefix("DB_HOST") == "DB"


def test_extract_prefix_no_separator():
    assert _extract_prefix("HOSTNAME") == "__ungrouped__"


def test_extract_prefix_custom_separator():
    assert _extract_prefix("APP.HOST", separator=".") == "APP"


# --- group_diff_by_prefix ---

def test_group_diff_empty_result():
    groups = group_diff_by_prefix(_result())
    assert groups == {}


def test_group_diff_missing_in_right():
    r = _result(missing_right=["DB_HOST", "DB_PORT"])
    groups = group_diff_by_prefix(r)
    assert "DB" in groups
    assert groups["DB"].missing_in_right == ["DB_HOST", "DB_PORT"]


def test_group_diff_mismatched():
    r = _result(mismatched={"APP_ENV": ("dev", "prod"), "APP_DEBUG": ("1", "0")})
    groups = group_diff_by_prefix(r)
    assert "APP" in groups
    assert set(groups["APP"].mismatched) == {"APP_ENV", "APP_DEBUG"}


def test_group_diff_ungrouped_excluded():
    r = _result(missing_right=["HOSTNAME"])
    groups = group_diff_by_prefix(r, include_ungrouped=False)
    assert "__ungrouped__" not in groups


def test_group_diff_ungrouped_included_by_default():
    r = _result(missing_right=["HOSTNAME"])
    groups = group_diff_by_prefix(r)
    assert "__ungrouped__" in groups


def test_group_summary_is_clean():
    grp = GroupSummary(prefix="DB")
    assert grp.is_clean is True
    grp.missing_in_right.append("DB_HOST")
    assert grp.is_clean is False


def test_group_summary_issue_count():
    grp = GroupSummary(
        prefix="X",
        missing_in_right=["X_A"],
        missing_in_left=["X_B"],
        mismatched=["X_C", "X_D"],
    )
    assert grp.issue_count == 4


# --- top_problem_groups ---

def test_top_problem_groups_ordering():
    r = _result(
        missing_right=["DB_HOST"],
        mismatched={"APP_ENV": ("a", "b"), "APP_DEBUG": ("1", "0")},
    )
    groups = group_diff_by_prefix(r)
    ranked = top_problem_groups(groups)
    assert ranked[0].prefix == "APP"


def test_top_problem_groups_limit():
    r = _result(missing_right=["DB_HOST", "APP_ENV", "CACHE_URL"])
    groups = group_diff_by_prefix(r)
    ranked = top_problem_groups(groups, limit=2)
    assert len(ranked) == 2


# --- format_group_report ---

def test_format_group_report_no_groups():
    report = format_group_report({}, color=False)
    assert "No groups found" in report


def test_format_group_report_shows_prefix():
    r = _result(missing_right=["DB_HOST"])
    groups = group_diff_by_prefix(r)
    report = format_group_report(groups, color=False)
    assert "DB" in report
    assert "DB_HOST" in report


def test_format_group_report_custom_title():
    report = format_group_report({}, color=False, title="My Report")
    assert "My Report" in report


def test_print_group_report_writes_to_file():
    r = _result(missing_right=["DB_HOST"])
    groups = group_diff_by_prefix(r)
    buf = io.StringIO()
    print_group_report(groups, color=False, file=buf)
    assert "DB" in buf.getvalue()
