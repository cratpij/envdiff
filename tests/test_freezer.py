"""Tests for envdiff.freezer and envdiff.freeze_reporter."""
from __future__ import annotations

import io
import os
import tempfile

import pytest

from envdiff.freezer import (
    FreezeResult,
    _checksum,
    detect_drift,
    detect_drift_from_file,
    freeze_env,
    freeze_env_file,
)
from envdiff.freeze_reporter import format_freeze_report, print_freeze_report


# ---------------------------------------------------------------------------
# freeze_env
# ---------------------------------------------------------------------------

def test_freeze_env_stores_copy():
    env = {"A": "1", "B": "2"}
    result = freeze_env(env)
    assert result.frozen == env
    assert result.frozen is not env  # deep copy


def test_freeze_env_checksum_is_hex():
    result = freeze_env({"X": "hello"})
    assert len(result.checksum) == 64  # sha256 hex
    int(result.checksum, 16)  # must be valid hex


def test_freeze_env_no_drift_by_default():
    result = freeze_env({"K": "v"})
    assert not result.has_drift
    assert result.drifted_keys == []
    assert result.added_keys == []
    assert result.removed_keys == []


def test_freeze_env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("FOO=bar\nBAZ=qux\n")
    result = freeze_env_file(str(p))
    assert result.frozen == {"FOO": "bar", "BAZ": "qux"}
    assert result.path == str(p)


# ---------------------------------------------------------------------------
# detect_drift
# ---------------------------------------------------------------------------

def test_detect_drift_no_change():
    baseline = freeze_env({"A": "1", "B": "2"}, path="base")
    result = detect_drift(baseline, {"A": "1", "B": "2"})
    assert not result.has_drift


def test_detect_drift_changed_value():
    baseline = freeze_env({"A": "old"}, path="base")
    result = detect_drift(baseline, {"A": "new"})
    assert result.drifted_keys == ["A"]
    assert result.has_drift


def test_detect_drift_added_key():
    baseline = freeze_env({"A": "1"}, path="base")
    result = detect_drift(baseline, {"A": "1", "B": "2"})
    assert result.added_keys == ["B"]
    assert not result.drifted_keys


def test_detect_drift_removed_key():
    baseline = freeze_env({"A": "1", "B": "2"}, path="base")
    result = detect_drift(baseline, {"A": "1"})
    assert result.removed_keys == ["B"]


def test_detect_drift_from_file(tmp_path):
    baseline = freeze_env({"FOO": "original"}, path="base")
    p = tmp_path / ".env"
    p.write_text("FOO=changed\n")
    result = detect_drift_from_file(baseline, str(p))
    assert result.drifted_keys == ["FOO"]


# ---------------------------------------------------------------------------
# FreezeResult.summary
# ---------------------------------------------------------------------------

def test_summary_no_drift():
    r = FreezeResult(path="x.env", frozen={}, checksum="abc")
    assert "no drift" in r.summary()


def test_summary_with_drift():
    r = FreezeResult(
        path="x.env", frozen={}, checksum="abc",
        drifted_keys=["A"], added_keys=["B", "C"], removed_keys=[]
    )
    s = r.summary()
    assert "1 changed" in s
    assert "2 added" in s


# ---------------------------------------------------------------------------
# freeze_reporter
# ---------------------------------------------------------------------------

def _clean_result() -> FreezeResult:
    return FreezeResult(path="prod.env", frozen={"A": "1"}, checksum="a" * 64)


def _drift_result() -> FreezeResult:
    return FreezeResult(
        path="prod.env",
        frozen={"A": "old", "B": "gone"},
        checksum="b" * 64,
        drifted_keys=["A"],
        added_keys=["C"],
        removed_keys=["B"],
    )


def test_format_no_drift_contains_ok():
    report = format_freeze_report(_clean_result(), color=False)
    assert "No drift" in report


def test_format_drift_shows_changed_key():
    report = format_freeze_report(_drift_result(), color=False)
    assert "~ A" in report


def test_format_drift_shows_added_key():
    report = format_freeze_report(_drift_result(), color=False)
    assert "+ C" in report


def test_format_drift_shows_removed_key():
    report = format_freeze_report(_drift_result(), color=False)
    assert "- B" in report


def test_format_includes_checksum():
    report = format_freeze_report(_clean_result(), color=False)
    assert "Checksum" in report


def test_print_freeze_report_writes_to_stream():
    buf = io.StringIO()
    print_freeze_report(_clean_result(), color=False, file=buf)
    assert "prod.env" in buf.getvalue()
