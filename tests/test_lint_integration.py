"""Integration tests: lint a real file on disk and report."""

from __future__ import annotations

import io

import pytest

from envdiff.linter import lint_env_file
from envdiff.lint_reporter import format_lint_report, print_lint_report


@pytest.fixture()
def good_env(tmp_path):
    p = tmp_path / ".env"
    p.write_text("DATABASE_URL=postgres://localhost/db\nSECRET_KEY=supersecret\n")
    return str(p)


@pytest.fixture()
def bad_env(tmp_path):
    p = tmp_path / ".env.bad"
    p.write_text(
        "database_url=postgres://localhost/db\n"  # lowercase key
        "SECRET_KEY=\n"                           # empty value
        "DUPLICATE=1\n"
        "DUPLICATE=2\n"                           # duplicate
        "NOEQUALSSIGN\n"                          # missing =
    )
    return str(p)


def test_good_env_no_errors(good_env):
    result = lint_env_file(good_env)
    assert not result.has_errors
    assert not result.has_warnings
    assert not result.issues


def test_bad_env_has_errors(bad_env):
    result = lint_env_file(bad_env)
    assert result.has_errors


def test_bad_env_lowercase_warning(bad_env):
    result = lint_env_file(bad_env)
    assert any("uppercase" in i.message for i in result.issues)


def test_bad_env_empty_value_info(bad_env):
    result = lint_env_file(bad_env)
    assert any(i.severity == "info" and "empty value" in i.message for i in result.issues)


def test_bad_env_duplicate_error(bad_env):
    result = lint_env_file(bad_env)
    assert any("Duplicate" in i.message for i in result.issues)


def test_bad_env_missing_equals_error(bad_env):
    result = lint_env_file(bad_env)
    assert any("'='" in i.message for i in result.issues)


def test_report_integration(bad_env):
    result = lint_env_file(bad_env)
    buf = io.StringIO()
    print_lint_report(result, filename=bad_env, use_color=False, output=buf)
    text = buf.getvalue()
    assert "error(s)" in text
    assert bad_env in text


def test_format_report_clean_file(good_env):
    result = lint_env_file(good_env)
    report = format_lint_report(result, filename=good_env, use_color=False)
    assert "No issues found" in report
