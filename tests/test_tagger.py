"""Tests for envdiff.tagger and envdiff.tag_reporter."""
from __future__ import annotations

import pytest

from envdiff.tagger import (
    TagResult,
    KNOWN_TAGS,
    tag_env,
    tag_env_file,
)
from envdiff.tag_reporter import format_tag_report


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _env() -> dict:
    return {
        "DATABASE_URL": "postgres://localhost/db",
        "SECRET_KEY": "s3cr3t",
        "DEBUG": "true",
        "LEGACY_FLAG": "1",
        "INTERNAL_TOKEN": "tok",
    }


# ---------------------------------------------------------------------------
# TagResult
# ---------------------------------------------------------------------------

def test_tag_result_keys_with_tag():
    r = TagResult(source="test")
    r.tags = {"A": {"required"}, "B": {"optional"}, "C": {"required"}}
    assert sorted(r.keys_with_tag("required")) == ["A", "C"]


def test_tag_result_tags_for_missing_key():
    r = TagResult(source="test")
    assert r.tags_for("MISSING") == set()


def test_tag_result_has_tag():
    r = TagResult(source="test")
    r.tags = {"X": {"secret"}}
    assert r.has_tag("X", "secret") is True
    assert r.has_tag("X", "required") is False


def test_tag_result_summary_empty():
    r = TagResult(source="test")
    assert r.summary() == "No keys tagged."


def test_tag_result_summary_with_tags():
    r = TagResult(source="test")
    r.tags = {"A": {"required"}, "B": {"required"}, "C": {"secret"}}
    s = r.summary()
    assert "3 key(s) tagged" in s
    assert "required=2" in s
    assert "secret=1" in s


# ---------------------------------------------------------------------------
# tag_env
# ---------------------------------------------------------------------------

def test_tag_env_basic():
    env = _env()
    tag_map = {"DATABASE_URL": ["required"], "SECRET_KEY": ["secret", "required"]}
    result = tag_env(env, tag_map, source="test")
    assert "required" in result.tags["DATABASE_URL"]
    assert "secret" in result.tags["SECRET_KEY"]
    assert "required" in result.tags["SECRET_KEY"]


def test_tag_env_skips_missing_keys():
    env = {"A": "1"}
    tag_map = {"A": ["required"], "MISSING": ["optional"]}
    result = tag_env(env, tag_map)
    assert "MISSING" not in result.tags
    assert "A" in result.tags


def test_tag_env_records_unknown_tags():
    env = {"A": "1"}
    tag_map = {"A": ["required", "custom_tag"]}
    result = tag_env(env, tag_map)
    assert "custom_tag" in result.unknown_tags
    assert "required" in result.tags.get("A", set())


def test_tag_env_unknown_only_tag_not_added():
    env = {"A": "1"}
    tag_map = {"A": ["bogus"]}
    result = tag_env(env, tag_map)
    # key has no valid tags so should not appear in result.tags
    assert "A" not in result.tags
    assert "bogus" in result.unknown_tags


def test_tag_env_source_default():
    result = tag_env({}, {})
    assert result.source == "<dict>"


def test_tag_env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("API_KEY=abc\nDEBUG=true\n")
    result = tag_env_file(str(f), {"API_KEY": ["secret"], "DEBUG": ["optional"]})
    assert result.source == str(f)
    assert "secret" in result.tags["API_KEY"]
    assert "optional" in result.tags["DEBUG"]


# ---------------------------------------------------------------------------
# format_tag_report
# ---------------------------------------------------------------------------

def test_format_report_no_tags():
    r = TagResult(source="empty.env")
    report = format_tag_report(r, use_color=False)
    assert "No tagged keys found" in report


def test_format_report_shows_tag_sections():
    r = TagResult(source="app.env")
    r.tags = {"DB_URL": {"required"}, "TOKEN": {"secret"}}
    report = format_tag_report(r, use_color=False)
    assert "REQUIRED" in report
    assert "SECRET" in report
    assert "DB_URL" in report
    assert "TOKEN" in report


def test_format_report_shows_unknown_tags():
    r = TagResult(source="app.env", unknown_tags=["fancy"])
    report = format_tag_report(r, use_color=False)
    assert "fancy" in report
    assert "Unknown tags" in report


def test_format_report_includes_summary():
    r = TagResult(source="app.env")
    r.tags = {"A": {"required"}}
    report = format_tag_report(r, use_color=False)
    assert "1 key(s) tagged" in report
