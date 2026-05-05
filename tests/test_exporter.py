"""Tests for envdiff.exporter — JSON, CSV, and Markdown export."""

from __future__ import annotations

import csv
import io
import json

import pytest

from envdiff.diff import EnvDiffResult
from envdiff.exporter import export, export_csv, export_json, export_markdown


def _make_result(
    missing_in_right=None,
    missing_in_left=None,
    mismatched=None,
) -> EnvDiffResult:
    return EnvDiffResult(
        missing_in_right=set(missing_in_right or []),
        missing_in_left=set(missing_in_left or []),
        mismatched=dict(mismatched or {}),
    )


# ---------------------------------------------------------------------------
# JSON
# ---------------------------------------------------------------------------

def test_export_json_empty():
    result = _make_result()
    data = json.loads(export_json(result))
    assert data == {"missing_in_right": [], "missing_in_left": [], "mismatched": {}}


def test_export_json_full():
    result = _make_result(
        missing_in_right=["FOO"],
        missing_in_left=["BAR"],
        mismatched={"BAZ": ("old", "new")},
    )
    data = json.loads(export_json(result))
    assert data["missing_in_right"] == ["FOO"]
    assert data["missing_in_left"] == ["BAR"]
    assert data["mismatched"]["BAZ"] == {"left": "old", "right": "new"}


# ---------------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------------

def test_export_csv_headers():
    result = _make_result()
    rows = list(csv.reader(io.StringIO(export_csv(result))))
    assert rows[0] == ["key", "status", "left_value", "right_value"]


def test_export_csv_rows():
    result = _make_result(
        missing_in_right=["ALPHA"],
        missing_in_left=["BETA"],
        mismatched={"GAMMA": ("x", "y")},
    )
    rows = list(csv.reader(io.StringIO(export_csv(result))))
    statuses = {r[0]: r[1] for r in rows[1:]}
    assert statuses["ALPHA"] == "missing_in_right"
    assert statuses["BETA"] == "missing_in_left"
    assert statuses["GAMMA"] == "mismatched"


# ---------------------------------------------------------------------------
# Markdown
# ---------------------------------------------------------------------------

def test_export_markdown_no_diff():
    result = _make_result()
    md = export_markdown(result)
    assert "no differences" in md


def test_export_markdown_contains_keys():
    result = _make_result(
        missing_in_right=["KEY_A"],
        mismatched={"KEY_B": ("v1", "v2")},
    )
    md = export_markdown(result)
    assert "KEY_A" in md
    assert "KEY_B" in md
    assert "missing in right" in md
    assert "mismatched" in md


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

def test_export_dispatch_json():
    result = _make_result()
    assert export(result, "json").startswith("{")


def test_export_dispatch_csv():
    result = _make_result()
    assert "key,status" in export(result, "csv")


def test_export_dispatch_markdown():
    result = _make_result()
    assert "|" in export(result, "markdown")


def test_export_dispatch_invalid():
    result = _make_result()
    with pytest.raises(ValueError, match="Unsupported export format"):
        export(result, "xml")  # type: ignore[arg-type]
