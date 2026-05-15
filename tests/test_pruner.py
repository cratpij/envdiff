"""Tests for envdiff.pruner and envdiff.prune_reporter."""
from __future__ import annotations

import io
import pathlib

import pytest

from envdiff.pruner import PruneResult, prune_env, prune_env_files
from envdiff.prune_reporter import format_prune_report, print_prune_report


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _result(
    original=None,
    reference=None,
    removed=None,
    kept=None,
) -> PruneResult:
    original = original or {"A": "1", "B": "2", "C": "3"}
    reference = reference or {"A": "1", "B": "2"}
    res = prune_env(original, reference, source_name="src", reference_name="ref")
    return res


# ---------------------------------------------------------------------------
# prune_env
# ---------------------------------------------------------------------------

def test_prune_env_removes_keys_not_in_reference():
    result = prune_env({"A": "1", "B": "2", "X": "99"}, {"A": "x", "B": "y"})
    assert "X" not in result.pruned
    assert "X" in result.removed_keys


def test_prune_env_keeps_reference_keys():
    result = prune_env({"A": "1", "B": "2"}, {"A": "x", "B": "y"})
    assert result.pruned == {"A": "1", "B": "2"}
    assert result.removed_keys == []


def test_prune_env_preserves_values():
    result = prune_env({"A": "hello", "Z": "gone"}, {"A": "ignored"})
    assert result.pruned["A"] == "hello"


def test_prune_env_total_removed():
    result = prune_env({"A": "1", "B": "2", "C": "3"}, {"A": "x"})
    assert result.total_removed == 2


def test_prune_env_extra_keys_preserved():
    result = prune_env(
        {"A": "1", "EXTRA": "keep", "Z": "drop"},
        {"A": "x"},
        extra_keys={"EXTRA"},
    )
    assert "EXTRA" in result.pruned
    assert "Z" not in result.pruned


def test_prune_env_empty_env():
    result = prune_env({}, {"A": "1"})
    assert result.pruned == {}
    assert result.removed_keys == []
    assert result.kept_keys == []


def test_prune_env_empty_reference_removes_all():
    result = prune_env({"A": "1", "B": "2"}, {})
    assert result.pruned == {}
    assert sorted(result.removed_keys) == ["A", "B"]


def test_prune_env_original_unchanged():
    env = {"A": "1", "B": "2"}
    prune_env(env, {"A": "x"})
    assert "B" in env  # original not mutated


# ---------------------------------------------------------------------------
# summary
# ---------------------------------------------------------------------------

def test_summary_nothing_pruned():
    result = prune_env({"A": "1"}, {"A": "x"}, source_name="s", reference_name="r")
    assert "No keys pruned" in result.summary()


def test_summary_lists_removed_keys():
    result = prune_env({"A": "1", "Z": "99"}, {"A": "x"}, source_name="s", reference_name="r")
    assert "Z" in result.summary()
    assert "1 key" in result.summary()


# ---------------------------------------------------------------------------
# prune_env_files
# ---------------------------------------------------------------------------

def test_prune_env_files(tmp_path: pathlib.Path):
    src = tmp_path / ".env.src"
    ref = tmp_path / ".env.ref"
    src.write_text("A=1\nB=2\nOBSOLETE=99\n")
    ref.write_text("A=x\nB=y\n")
    result = prune_env_files(str(src), str(ref))
    assert "OBSOLETE" in result.removed_keys
    assert "A" in result.pruned


# ---------------------------------------------------------------------------
# reporter
# ---------------------------------------------------------------------------

def test_format_prune_report_includes_header():
    result = _result()
    report = format_prune_report(result, use_color=False)
    assert "Prune Report" in report


def test_format_prune_report_shows_removed_key():
    result = prune_env({"A": "1", "GONE": "x"}, {"A": "y"}, source_name="s", reference_name="r")
    report = format_prune_report(result, use_color=False)
    assert "GONE" in report


def test_format_prune_report_nothing_pruned_message():
    result = prune_env({"A": "1"}, {"A": "y"}, source_name="s", reference_name="r")
    report = format_prune_report(result, use_color=False)
    assert "nothing pruned" in report.lower()


def test_format_prune_report_filename_override():
    result = _result()
    report = format_prune_report(result, filename="custom.env", use_color=False)
    assert "custom.env" in report


def test_print_prune_report_writes_to_stream():
    result = _result()
    buf = io.StringIO()
    print_prune_report(result, use_color=False, file=buf)
    assert "Prune Report" in buf.getvalue()
