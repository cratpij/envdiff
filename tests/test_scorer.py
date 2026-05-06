"""Tests for envdiff.scorer."""
import pytest
from unittest.mock import MagicMock

from envdiff.scorer import (
    EnvScore,
    score_from_profile,
    score_from_lint,
    score_from_validation,
    compute_score,
)


def _mock_profile(empty=(), long=()):
    p = MagicMock()
    p.empty_value_keys = list(empty)
    p.long_value_keys = list(long)
    return p


def _mock_lint(errors=0, warnings=0):
    issues = []
    for _ in range(errors):
        i = MagicMock()
        i.severity = "error"
        issues.append(i)
    for _ in range(warnings):
        i = MagicMock()
        i.severity = "warning"
        issues.append(i)
    r = MagicMock()
    r.issues = issues
    return r


def _mock_validation(missing=()):
    v = MagicMock()
    v.missing_required = list(missing)
    return v


def test_env_score_defaults():
    s = EnvScore(path=".env")
    assert s.score == 100
    assert s.grade == "A"
    assert s.is_healthy()


def test_env_score_grade_boundaries():
    s = EnvScore(path=".env", deductions={"x": 11})
    assert s.score == 89
    assert s.grade == "B"

    s2 = EnvScore(path=".env", deductions={"x": 26})
    assert s2.score == 74
    assert s2.grade == "C"

    s3 = EnvScore(path=".env", deductions={"x": 61})
    assert s3.score == 39
    assert s3.grade == "F"


def test_score_never_goes_below_zero():
    s = EnvScore(path=".env", deductions={"a": 60, "b": 60})
    assert s.score == 0


def test_score_from_profile_empty_values():
    s = EnvScore(path=".env")
    score_from_profile(s, _mock_profile(empty=["A", "B"]))
    assert "empty_values" in s.deductions
    assert s.deductions["empty_values"] == 8
    assert len(s.notes) == 1


def test_score_from_profile_no_issues():
    s = EnvScore(path=".env")
    score_from_profile(s, _mock_profile())
    assert s.deductions == {}
    assert s.notes == []


def test_score_from_lint_errors_and_warnings():
    s = EnvScore(path=".env")
    score_from_lint(s, _mock_lint(errors=2, warnings=3))
    assert "lint_errors" in s.deductions
    assert "lint_warnings" in s.deductions


def test_score_from_validation_missing_required():
    s = EnvScore(path=".env")
    score_from_validation(s, _mock_validation(missing=["DB_URL", "SECRET"]))
    assert "missing_required" in s.deductions
    assert s.deductions["missing_required"] == 12


def test_compute_score_clean():
    result = compute_score(
        ".env",
        _mock_profile(),
        _mock_lint(),
        _mock_validation(),
    )
    assert result.score == 100
    assert result.grade == "A"


def test_compute_score_combined_deductions():
    result = compute_score(
        ".env",
        _mock_profile(empty=["X"]),
        _mock_lint(errors=1),
        _mock_validation(missing=["Y"]),
    )
    assert result.score < 100
    assert len(result.notes) == 3
