"""Tests for envdiff.audit_reporter."""

import pytest
from envdiff.auditor import AuditResult
from envdiff.linter import LintResult, LintIssue
from envdiff.profiler import EnvProfile
from envdiff.validator import ValidationResult
from envdiff.scorer import EnvScore
from envdiff.audit_reporter import format_audit_report, format_multi_audit_report


def _result(score=90.0, errors=0, missing=None, empty=0, total=3):
    issues = [LintIssue(line_number=1, key="K", level="error", message="e")] * errors
    return AuditResult(
        path="test.env",
        lint=LintResult(issues=issues),
        profile=EnvProfile(
            total_keys=total, empty_count=empty, long_value_keys=[],
            max_value_key=None, max_value_length=0,
        ),
        validation=ValidationResult(
            missing_required=missing or [], extra_keys=[],
        ),
        score=EnvScore(score=score, deductions=[]),
    )


def test_format_pass_contains_pass():
    report = format_audit_report(_result(score=90), color=False)
    assert "PASS" in report


def test_format_fail_contains_fail():
    report = format_audit_report(_result(score=90, errors=1), color=False)
    assert "FAIL" in report


def test_format_shows_score():
    report = format_audit_report(_result(score=78), color=False)
    assert "78" in report


def test_format_shows_path():
    report = format_audit_report(_result(), color=False)
    assert "test.env" in report


def test_format_shows_lint_errors():
    report = format_audit_report(_result(errors=2), color=False)
    assert "2 error" in report


def test_format_shows_validation_issue():
    report = format_audit_report(_result(missing=["DB_URL"]), color=False)
    assert "DB_URL" in report or "issues" in report


def test_format_multi_shows_summary():
    results = [_result(score=90), _result(score=85)]
    report = format_multi_audit_report(results, color=False)
    assert "2/2" in report


def test_format_multi_partial_pass_summary():
    results = [_result(score=90), _result(score=90, errors=1)]
    report = format_multi_audit_report(results, color=False)
    assert "1/2" in report


def test_format_with_color_does_not_raise():
    report = format_audit_report(_result(), color=True)
    assert "test.env" in report
