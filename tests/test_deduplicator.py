"""Tests for envdiff.deduplicator and envdiff.dedup_reporter."""

from __future__ import annotations

from pathlib import Path

import pytest

from envdiff.deduplicator import (
    DeduplicationResult,
    deduplicate_env,
    deduplicate_env_file,
    find_duplicates,
)
from envdiff.dedup_reporter import format_dedup_report


# ---------------------------------------------------------------------------
# find_duplicates
# ---------------------------------------------------------------------------

def test_find_duplicates_no_dupes():
    lines = ["A=1", "B=2", "C=3"]
    dupes, deduped = find_duplicates(lines)
    assert dupes == {}
    assert deduped == {"A": "1", "B": "2", "C": "3"}


def test_find_duplicates_single_dupe():
    lines = ["A=1", "A=2"]
    dupes, deduped = find_duplicates(lines)
    assert "A" in dupes
    assert dupes["A"] == ["1", "2"]
    assert deduped["A"] == "2"  # last wins


def test_find_duplicates_skips_comments_and_blanks():
    lines = ["# comment", "", "A=hello", "A=world"]
    dupes, _ = find_duplicates(lines)
    assert "A" in dupes
    assert len(dupes["A"]) == 2


def test_find_duplicates_skips_malformed_lines():
    lines = ["NOEQUALS", "A=1"]
    dupes, deduped = find_duplicates(lines)
    assert dupes == {}
    assert "A" in deduped


def test_find_duplicates_strips_quotes():
    lines = ['KEY="value1"', "KEY='value2'"]
    dupes, deduped = find_duplicates(lines)
    assert dupes["KEY"] == ["value1", "value2"]
    assert deduped["KEY"] == "value2"


# ---------------------------------------------------------------------------
# DeduplicationResult
# ---------------------------------------------------------------------------

def _make_result(dupes=None):
    dupes = dupes or {}
    deduped = {k: v[-1] for k, v in dupes.items()}
    return DeduplicationResult(source="test.env", duplicates=dupes, deduped=deduped)


def test_has_duplicates_false_when_empty():
    r = _make_result()
    assert not r.has_duplicates()


def test_has_duplicates_true_when_present():
    r = _make_result({"KEY": ["a", "b"]})
    assert r.has_duplicates()


def test_summary_clean():
    r = _make_result()
    assert "no duplicate" in r.summary()


def test_summary_with_dupes():
    r = _make_result({"KEY": ["a", "b"]})
    assert "KEY" in r.summary()
    assert "1 duplicate" in r.summary()


# ---------------------------------------------------------------------------
# deduplicate_env
# ---------------------------------------------------------------------------

def test_deduplicate_env_returns_result():
    result = deduplicate_env(["A=1", "B=2"])
    assert isinstance(result, DeduplicationResult)
    assert not result.has_duplicates()


def test_deduplicate_env_detects_dupes():
    result = deduplicate_env(["X=foo", "X=bar"], source="my.env")
    assert result.has_duplicates()
    assert result.source == "my.env"


# ---------------------------------------------------------------------------
# deduplicate_env_file
# ---------------------------------------------------------------------------

def test_deduplicate_env_file(tmp_path: Path):
    env = tmp_path / ".env"
    env.write_text("A=1\nB=2\nA=3\n")
    result = deduplicate_env_file(env)
    assert result.has_duplicates()
    assert result.deduped["A"] == "3"


def test_deduplicate_env_file_not_found(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        deduplicate_env_file(tmp_path / "missing.env")


# ---------------------------------------------------------------------------
# format_dedup_report
# ---------------------------------------------------------------------------

def test_format_no_dupes_contains_ok_message():
    r = _make_result()
    report = format_dedup_report(r, color=False)
    assert "No duplicate" in report


def test_format_dupes_shows_key():
    r = _make_result({"SECRET": ["old", "new"]})
    report = format_dedup_report(r, color=False)
    assert "SECRET" in report
    assert "2 occurrences" in report


def test_format_shows_winning_value():
    r = _make_result({"DB_URL": ["postgres://a", "postgres://b"]})
    report = format_dedup_report(r, color=False)
    assert "postgres://b" in report


def test_format_custom_filename():
    r = _make_result()
    report = format_dedup_report(r, color=False, filename="prod.env")
    assert "prod.env" in report
