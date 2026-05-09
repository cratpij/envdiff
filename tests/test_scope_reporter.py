"""Tests for envdiff.scope_reporter."""
import pytest

from envdiff.scoper import Scope, scope_diff
from envdiff.scope_reporter import format_scope_report, print_scope_report


def _clean_result():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    scope = Scope(name="db", patterns=["DB_*"])
    return scope_diff(env, env.copy(), scope)


def _diff_result():
    left = {"DB_HOST": "localhost", "DB_PORT": "5432", "API_KEY": "abc"}
    right = {"DB_HOST": "prod.db", "DB_PORT": "5432", "SECRET": "xyz"}
    scope = Scope(name="db", patterns=["DB_*"])
    return scope_diff(left, right, scope)


def test_format_includes_scope_name():
    report = format_scope_report(_clean_result(), color=False)
    assert "db" in report


def test_format_clean_shows_no_differences():
    report = format_scope_report(_clean_result(), color=False)
    assert "No differences" in report


def test_format_mismatch_shown():
    report = format_scope_report(_diff_result(), color=False)
    assert "DB_HOST" in report
    assert "MISMATCH" in report


def test_format_excluded_keys_note_shown():
    report = format_scope_report(_diff_result(), color=False)
    assert "outside scope" in report


def test_format_uses_custom_left_right_names():
    report = format_scope_report(
        _diff_result(), left_name="staging", right_name="production", color=False
    )
    assert "staging" in report
    assert "production" in report


def test_format_missing_in_right_shown():
    left = {"DB_HOST": "localhost", "DB_EXTRA": "val"}
    right = {"DB_HOST": "localhost"}
    scope = Scope(name="db", patterns=["DB_*"])
    result = scope_diff(left, right, scope)
    report = format_scope_report(result, right_name="prod", color=False)
    assert "MISSING" in report
    assert "prod" in report


def test_format_no_color_has_no_escape_codes():
    report = format_scope_report(_diff_result(), color=False)
    assert "\033[" not in report


def test_format_with_color_has_escape_codes():
    report = format_scope_report(_diff_result(), color=True)
    assert "\033[" in report


def test_print_scope_report_outputs_to_stdout(capsys):
    print_scope_report(_clean_result(), color=False)
    captured = capsys.readouterr()
    assert "db" in captured.out
    assert "No differences" in captured.out
