"""Tests for envdiff.linter."""

from __future__ import annotations

import pytest

from envdiff.linter import LintIssue, LintResult, lint_lines, lint_env_file


def _lines(*lines: str) -> list[str]:
    return [l + "\n" for l in lines]


# --- LintResult helpers ---

def test_lint_result_no_issues_has_no_errors():
    result = LintResult()
    assert not result.has_errors
    assert not result.has_warnings


def test_lint_result_summary_clean():
    assert LintResult().summary() == "No lint issues found."


def test_lint_result_summary_with_issues():
    result = LintResult(issues=[
        LintIssue(1, "A", "msg", "error"),
        LintIssue(2, "B", "msg", "warning"),
        LintIssue(3, "C", "msg", "warning"),
    ])
    assert "1 error(s)" in result.summary()
    assert "2 warning(s)" in result.summary()


# --- lint_lines ---

def test_lint_lines_clean_file():
    result = lint_lines(_lines("FOO=bar", "BAZ=qux"))
    assert not result.issues


def test_lint_lines_skips_comments_and_blanks():
    result = lint_lines(_lines("# comment", "", "KEY=value"))
    assert not result.issues


def test_lint_lines_missing_equals():
    result = lint_lines(_lines("NODIVIDER"))
    assert any(i.severity == "error" and "'='" in i.message for i in result.issues)


def test_lint_lines_empty_key():
    result = lint_lines(_lines("=value"))
    assert any("Empty key" in i.message for i in result.issues)


def test_lint_lines_lowercase_key_warning():
    result = lint_lines(_lines("my_key=value"))
    assert any(i.severity == "warning" and "uppercase" in i.message for i in result.issues)


def test_lint_lines_key_with_spaces_error():
    result = lint_lines(_lines("MY KEY=value"))
    assert any(i.severity == "error" and "spaces" in i.message for i in result.issues)


def test_lint_lines_empty_value_info():
    result = lint_lines(_lines("EMPTY_KEY="))
    assert any(i.severity == "info" and "empty value" in i.message for i in result.issues)


def test_lint_lines_duplicate_key_error():
    result = lint_lines(_lines("FOO=1", "FOO=2"))
    errors = [i for i in result.issues if i.severity == "error" and "Duplicate" in i.message]
    assert len(errors) == 1
    assert errors[0].line_number == 2


def test_lint_lines_duplicate_key_reports_first_seen_line():
    result = lint_lines(_lines("FOO=1", "BAR=2", "FOO=3"))
    dup = next(i for i in result.issues if "Duplicate" in i.message)
    assert "line 1" in dup.message


def test_lint_lines_multiple_issues():
    result = lint_lines(_lines("bad key=v", "FOO=1", "FOO=2"))
    assert result.has_errors


# --- lint_env_file ---

def test_lint_env_file_not_found():
    result = lint_env_file("/nonexistent/path/.env")
    assert result.has_errors
    assert any("File not found" in i.message for i in result.issues)


def test_lint_env_file_reads_and_lints(tmp_path):
    env = tmp_path / ".env"
    env.write_text("FOO=bar\nBAZ=\n")
    result = lint_env_file(str(env))
    assert not result.has_errors
    assert any(i.severity == "info" for i in result.issues)  # empty BAZ
