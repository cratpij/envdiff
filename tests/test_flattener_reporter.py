"""Tests for envdiff.flattener_reporter."""

from envdiff.flattener import FlattenResult
from envdiff.flattener_reporter import format_flatten_report


def _clean() -> FlattenResult:
    return FlattenResult(
        flat={"APP_ENV": "dev", "DB_HOST": "localhost"},
        collisions={},
        sources={"APP_ENV": "base", "DB_HOST": "base"},
    )


def _with_collision() -> FlattenResult:
    return FlattenResult(
        flat={"DB_HOST": "prod-db", "SECRET": "abc"},
        collisions={"DB_HOST": ["base", "override"]},
        sources={"DB_HOST": "override", "SECRET": "override"},
    )


def test_format_includes_header():
    report = format_flatten_report(_clean(), use_color=False)
    assert "Flatten Report" in report


def test_format_includes_filename():
    report = format_flatten_report(_clean(), filename=".env.prod", use_color=False)
    assert ".env.prod" in report


def test_format_no_collisions_shows_summary():
    report = format_flatten_report(_clean(), use_color=False)
    assert "no collisions" in report


def test_format_shows_keys():
    report = format_flatten_report(_clean(), use_color=False)
    assert "APP_ENV" in report
    assert "DB_HOST" in report


def test_format_shows_source_label():
    report = format_flatten_report(_clean(), use_color=False)
    assert "from: base" in report


def test_format_collision_marker_shown():
    report = format_flatten_report(_with_collision(), use_color=False)
    assert "[COLLISION]" in report


def test_format_collision_section_shown():
    report = format_flatten_report(_with_collision(), use_color=False)
    assert "Collisions:" in report
    assert "DB_HOST" in report


def test_format_collision_lists_sources():
    report = format_flatten_report(_with_collision(), use_color=False)
    assert "base" in report
    assert "override" in report


def test_format_no_collision_section_when_clean():
    report = format_flatten_report(_clean(), use_color=False)
    assert "Collisions:" not in report


def test_format_with_color_does_not_crash():
    report = format_flatten_report(_with_collision(), use_color=True)
    assert "DB_HOST" in report
