"""Tests for envdiff.lint_reporter."""

from __future__ import annotations

import io

from envdiff.linter import LintIssue, LintResult
from envdiff.lint_reporter import format_lint_report, print_lint_report


def _result(*issues: LintIssue) -> LintResult:
    return LintResult(issues=list(issues))


def test_format_no_issues_contains_ok_message():
    report = format_lint_report(_result(), filename=".env")
    assert "No issues found" in report
    assert ".env" in report


def test_format_no_filename():
    report = format_lint_report(_result())
    assert "Lint report" in report
    assert ":" not in report.splitlines()[0]  # no colon when no filename


def test_format_shows_line_number():
    issue = LintIssue(5, "FOO", "Some error.", "error")
    report = format_lint_report(_result(issue), use_color=False)
    assert "line 5" in report


def test_format_shows_key():
    issue = LintIssue(2, "MY_KEY", "Has spaces.", "warning")
    report = format_lint_report(_result(issue), use_color=False)
    assert "[MY_KEY]" in report


def test_format_shows_no_key_bracket_when_key_is_none():
    issue = LintIssue(1, None, "Missing '='.", "error")
    report = format_lint_report(_result(issue), use_color=False)
    assert "[" not in report


def test_format_shows_severity_label():
    issue = LintIssue(3, "X", "Empty value.", "info")
    report = format_lint_report(_result(issue), use_color=False)
    assert "INFO" in report


def test_format_shows_summary():
    issues = [
        LintIssue(1, "A", "msg", "error"),
        LintIssue(2, "B", "msg", "warning"),
    ]
    report = format_lint_report(_result(*issues), use_color=False)
    assert "1 error(s)" in report
    assert "1 warning(s)" in report


def test_format_color_codes_present_when_enabled():
    issue = LintIssue(1, "K", "msg", "error")
    report = format_lint_report(_result(issue), use_color=True)
    assert "\033[" in report


def test_format_no_color_codes_when_disabled():
    issue = LintIssue(1, "K", "msg", "error")
    report = format_lint_report(_result(issue), use_color=False)
    assert "\033[" not in report


def test_print_lint_report_writes_to_output():
    issue = LintIssue(4, "BAD KEY", "Contains spaces.", "error")
    buf = io.StringIO()
    print_lint_report(_result(issue), filename="test.env", use_color=False, output=buf)
    output = buf.getvalue()
    assert "test.env" in output
    assert "line 4" in output
    assert "ERROR" in output
