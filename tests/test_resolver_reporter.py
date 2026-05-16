"""Tests for envdiff.resolver_reporter."""

from envdiff.resolver import resolve_envs
from envdiff.resolver_reporter import format_resolve_report


def _result():
    return resolve_envs(
        [
            {"HOST": "localhost", "PORT": "5432"},
            {"HOST": "prod.example.com", "API_KEY": "secret"},
        ],
        labels=["base", "prod"],
    )


def test_format_includes_header() -> None:
    report = format_resolve_report(_result(), filename=".env.prod")
    assert "Resolve Report" in report
    assert ".env.prod" in report


def test_format_shows_layers() -> None:
    report = format_resolve_report(_result())
    assert "base" in report
    assert "prod" in report


def test_format_shows_overridden_key() -> None:
    report = format_resolve_report(_result())
    assert "OVERRIDDEN" in report
    assert "HOST" in report


def test_format_shows_origin_label() -> None:
    report = format_resolve_report(_result())
    # prod wins for HOST
    assert "[prod]" in report


def test_format_shows_non_overridden_key() -> None:
    report = format_resolve_report(_result())
    assert "PORT" in report
    assert "[base]" in report


def test_format_shows_summary_line() -> None:
    report = format_resolve_report(_result())
    assert "resolved" in report
    assert "overridden" in report


def test_format_no_filename_uses_default() -> None:
    report = format_resolve_report(_result())
    assert "(resolved)" in report


def test_format_new_key_from_override_shown() -> None:
    report = format_resolve_report(_result())
    assert "API_KEY" in report
