"""Tests for envdiff.reporter formatting utilities."""

import io
import pytest

from envdiff.diff import EnvDiffResult
from envdiff.reporter import format_report, print_report


def _make_result(
    missing_in_right=None,
    missing_in_left=None,
    mismatched=None,
    left_name=".env.dev",
    right_name=".env.prod",
):
    return EnvDiffResult(
        left_name=left_name,
        right_name=right_name,
        missing_in_right=set(missing_in_right or []),
        missing_in_left=set(missing_in_left or []),
        mismatched=dict(mismatched or {}),
    )


def test_no_differences_message():
    result = _make_result()
    report = format_report(result, use_color=False)
    assert "No differences found." in report
    assert ".env.dev" in report
    assert ".env.prod" in report


def test_missing_in_right_shown():
    result = _make_result(missing_in_right=["SECRET_KEY", "DB_URL"])
    report = format_report(result, use_color=False)
    assert "Missing in .env.prod" in report
    assert "SECRET_KEY" in report
    assert "DB_URL" in report


def test_missing_in_left_shown():
    result = _make_result(missing_in_left=["NEW_FEATURE_FLAG"])
    report = format_report(result, use_color=False)
    assert "Missing in .env.dev" in report
    assert "NEW_FEATURE_FLAG" in report


def test_mismatched_values_shown():
    result = _make_result(mismatched={"LOG_LEVEL": ("DEBUG", "ERROR")})
    report = format_report(result, use_color=False)
    assert "Mismatched values" in report
    assert "LOG_LEVEL" in report
    assert "'DEBUG'" in report
    assert "'ERROR'" in report


def test_summary_line_present():
    result = _make_result(
        missing_in_right=["A"],
        mismatched={"B": ("1", "2")},
    )
    report = format_report(result, use_color=False)
    # summary() from EnvDiffResult should appear at the bottom
    assert result.summary() in report


def test_color_codes_included_when_enabled():
    result = _make_result(missing_in_right=["SOME_KEY"])
    report_color = format_report(result, use_color=True)
    report_plain = format_report(result, use_color=False)
    assert "\033[" in report_color
    assert "\033[" not in report_plain


def test_print_report_writes_to_stream():
    result = _make_result(missing_in_right=["TOKEN"])
    buf = io.StringIO()
    print_report(result, use_color=False, stream=buf)
    output = buf.getvalue()
    assert "TOKEN" in output
    assert ".env.dev" in output


def test_keys_sorted_in_output():
    result = _make_result(missing_in_right=["ZEBRA", "ALPHA", "MANGO"])
    report = format_report(result, use_color=False)
    idx_alpha = report.index("ALPHA")
    idx_mango = report.index("MANGO")
    idx_zebra = report.index("ZEBRA")
    assert idx_alpha < idx_mango < idx_zebra
