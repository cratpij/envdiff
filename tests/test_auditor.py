"""Tests for envdiff.auditor."""

import pytest
from unittest.mock import patch, MagicMock

from envdiff.auditor import AuditResult, audit_env_file
from envdiff.linter import LintResult, LintIssue
from envdiff.profiler import EnvProfile
from envdiff.validator import ValidationResult
from envdiff.scorer import EnvScore


def _make_lint(errors=0, warnings=0):
    issues = [LintIssue(line_number=1, key="K", level="error", message="e")] * errors
    issues += [LintIssue(line_number=2, key="K", level="warning", message="w")] * warnings
    return LintResult(issues=issues)


def _make_profile(total=3, empty=0):
    return EnvProfile(
        total_keys=total, empty_count=empty, long_value_keys=[],
        max_value_key=None, max_value_length=0,
    )


def _make_validation(missing=None, extra=None):
    return ValidationResult(
        missing_required=missing or [],
        extra_keys=extra or [],
    )


def _make_score(score=90.0):
    return EnvScore(score=score, deductions=[])


def test_audit_result_passed_when_all_ok():
    result = AuditResult(
        path=".env",
        lint=_make_lint(),
        profile=_make_profile(),
        validation=_make_validation(),
        score=_make_score(90),
    )
    assert result.passed is True


def test_audit_result_fails_on_lint_error():
    result = AuditResult(
        path=".env",
        lint=_make_lint(errors=1),
        profile=_make_profile(),
        validation=_make_validation(),
        score=_make_score(90),
    )
    assert result.passed is False


def test_audit_result_fails_on_validation_issue():
    result = AuditResult(
        path=".env",
        lint=_make_lint(),
        profile=_make_profile(),
        validation=_make_validation(missing=["REQUIRED_KEY"]),
        score=_make_score(90),
    )
    assert result.passed is False


def test_audit_result_fails_on_low_score():
    result = AuditResult(
        path=".env",
        lint=_make_lint(),
        profile=_make_profile(),
        validation=_make_validation(),
        score=_make_score(40),
    )
    assert result.passed is False


def test_audit_result_summary_contains_path():
    result = AuditResult(
        path="staging.env",
        lint=_make_lint(),
        profile=_make_profile(),
        validation=_make_validation(),
        score=_make_score(95),
    )
    assert "staging.env" in result.summary()


def test_audit_env_file_returns_audit_result(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("FOO=bar\nBAZ=qux\n")
    result = audit_env_file(str(env_file))
    assert isinstance(result, AuditResult)
    assert result.path == str(env_file)


def test_audit_env_file_empty_file_adds_note(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("")
    result = audit_env_file(str(env_file))
    assert any("empty" in n.lower() for n in result.notes)


def test_audit_env_file_with_required_keys(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("FOO=bar\n")
    result = audit_env_file(str(env_file), required_keys=["FOO", "MISSING"])
    assert not result.validation.is_valid()
    assert "MISSING" in result.validation.missing_required
