"""Tests for envdiff.digester and envdiff.digest_reporter."""

from __future__ import annotations

import io
import tempfile
import os

import pytest

from envdiff.digester import (
    DigestResult,
    digest_env,
    digest_env_file,
    _is_boolean,
    _is_numeric,
    _is_url,
)
from envdiff.digest_reporter import format_digest_report, print_digest_report


# ---------------------------------------------------------------------------
# Unit helpers
# ---------------------------------------------------------------------------

def test_is_numeric_integer():
    assert _is_numeric("42")


def test_is_numeric_float():
    assert _is_numeric("3.14")


def test_is_numeric_false():
    assert not _is_numeric("hello")


def test_is_boolean_true_variants():
    for v in ("true", "True", "TRUE", "yes", "1", "on", "false", "no", "0", "off"):
        assert _is_boolean(v), v


def test_is_boolean_false():
    assert not _is_boolean("maybe")


def test_is_url_http():
    assert _is_url("http://example.com")


def test_is_url_postgres():
    assert _is_url("postgres://user:pass@localhost/db")


def test_is_url_false():
    assert not _is_url("some_plain_value")


# ---------------------------------------------------------------------------
# digest_env
# ---------------------------------------------------------------------------

def test_digest_empty_env():
    result = digest_env({}, source="test")
    assert result.total_keys == 0
    assert not result.has_empty


def test_digest_categorises_empty_values():
    result = digest_env({"FOO": "", "BAR": "hello"}, source="t")
    assert "FOO" in result.empty_keys
    assert "BAR" not in result.empty_keys


def test_digest_categorises_booleans():
    result = digest_env({"FLAG": "true", "VAL": "hello"}, source="t")
    assert "FLAG" in result.boolean_keys
    assert "VAL" not in result.boolean_keys


def test_digest_categorises_numeric():
    result = digest_env({"PORT": "8080", "NAME": "app"}, source="t")
    assert "PORT" in result.numeric_keys


def test_digest_categorises_url():
    result = digest_env({"DB_URL": "postgres://localhost/db"}, source="t")
    assert "DB_URL" in result.url_keys


def test_digest_long_values():
    result = digest_env({"KEY": "x" * 101}, source="t", long_value_threshold=100)
    assert "KEY" in result.long_value_keys


def test_digest_short_value_not_long():
    result = digest_env({"KEY": "short"}, source="t", long_value_threshold=100)
    assert "KEY" not in result.long_value_keys


def test_digest_summary_contains_source():
    result = digest_env({}, source="myenv")
    assert "myenv" in result.summary()


def test_digest_summary_all_standard_message():
    result = digest_env({"KEY": "value"}, source="t")
    assert "standard" in result.summary()


def test_digest_type_breakdown_keys():
    result = digest_env({}, source="t")
    assert set(result.type_breakdown.keys()) == {"empty", "numeric", "boolean", "url", "long"}


# ---------------------------------------------------------------------------
# digest_env_file
# ---------------------------------------------------------------------------

def _write(content: str) -> str:
    fd, path = tempfile.mkstemp(suffix=".env")
    with os.fdopen(fd, "w") as f:
        f.write(content)
    return path


def test_digest_env_file_reads_file():
    path = _write("PORT=9000\nDEBUG=true\n")
    try:
        result = digest_env_file(path)
        assert result.total_keys == 2
        assert "PORT" in result.numeric_keys
        assert "DEBUG" in result.boolean_keys
    finally:
        os.unlink(path)


# ---------------------------------------------------------------------------
# format_digest_report
# ---------------------------------------------------------------------------

def _make_result(**kwargs) -> DigestResult:
    defaults = dict(
        source="test.env",
        total_keys=3,
        empty_keys=[],
        numeric_keys=[],
        boolean_keys=[],
        url_keys=[],
        long_value_keys=[],
    )
    defaults.update(kwargs)
    return DigestResult(**defaults)


def test_format_includes_header():
    result = _make_result()
    report = format_digest_report(result, use_color=False)
    assert "Digest Report" in report


def test_format_shows_empty_keys():
    result = _make_result(empty_keys=["MISSING"])
    report = format_digest_report(result, use_color=False)
    assert "MISSING" in report
    assert "empty" in report


def test_format_shows_url_keys():
    result = _make_result(url_keys=["DATABASE_URL"])
    report = format_digest_report(result, use_color=False)
    assert "DATABASE_URL" in report


def test_format_standard_message_when_no_special():
    result = _make_result()
    report = format_digest_report(result, use_color=False)
    assert "standard" in report


def test_print_digest_report_writes_to_file():
    result = _make_result()
    buf = io.StringIO()
    print_digest_report(result, use_color=False, file=buf)
    assert "Digest Report" in buf.getvalue()
