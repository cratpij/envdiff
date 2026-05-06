"""Tests for envdiff.score_reporter."""
import io

from envdiff.scorer import EnvScore
from envdiff.score_reporter import (
    format_score_report,
    format_multi_score_report,
    print_score_report,
)


def _score(path=".env", deductions=None, notes=None):
    s = EnvScore(path=path)
    if deductions:
        s.deductions = deductions
    if notes:
        s.notes = notes
    return s


def test_format_score_report_perfect():
    report = format_score_report(_score(), use_color=False)
    assert ".env" in report
    assert "100/100" in report
    assert "No issues found" in report


def test_format_score_report_with_deductions():
    s = _score(deductions={"lint_errors": 16}, notes=["2 lint error(s) (-16)"])
    report = format_score_report(s, use_color=False)
    assert "84/100" in report
    assert "2 lint error(s)" in report
    assert "Deductions" in report


def test_format_score_report_grade_shown():
    s = _score(deductions={"x": 15})
    report = format_score_report(s, use_color=False)
    assert "[B]" in report


def test_format_score_report_uses_color():
    report_color = format_score_report(_score(), use_color=True)
    report_plain = format_score_report(_score(), use_color=False)
    assert "\033[" in report_color
    assert "\033[" not in report_plain


def test_format_multi_score_report_average():
    scores = [
        _score(".env.dev", deductions={"x": 10}),
        _score(".env.prod", deductions={"x": 20}),
    ]
    report = format_multi_score_report(scores, use_color=False)
    assert "Average score: 85/100" in report
    assert ".env.dev" in report
    assert ".env.prod" in report


def test_format_multi_score_report_empty():
    report = format_multi_score_report([], use_color=False)
    assert "Average score: 0/100" in report


def test_print_score_report_writes_to_file():
    buf = io.StringIO()
    print_score_report(_score(), use_color=False, file=buf)
    output = buf.getvalue()
    assert "100/100" in output
    assert output.endswith("\n")
