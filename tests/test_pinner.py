"""Tests for envdiff.pinner and envdiff.pin_reporter."""
from __future__ import annotations

import json
import os
import textwrap
from io import StringIO
from pathlib import Path

import pytest

from envdiff.pinner import (
    PinnedEnv,
    pin_env,
    pin_env_file,
    save_pin,
    load_pin,
    diff_against_pin,
    diff_file_against_pin,
)
from envdiff.pin_reporter import format_pin_report, print_pin_report


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(textwrap.dedent(content))
    return p


# ---------------------------------------------------------------------------
# PinnedEnv dataclass
# ---------------------------------------------------------------------------

def test_pin_env_captures_values():
    env = {"A": "1", "B": "2"}
    pin = pin_env(env, source="test")
    assert pin.values == env
    assert pin.source == "test"
    assert pin.pinned_at  # non-empty timestamp


def test_pin_env_to_dict_roundtrip():
    env = {"X": "hello"}
    pin = pin_env(env)
    d = pin.to_dict()
    restored = PinnedEnv.from_dict(d)
    assert restored.values == pin.values
    assert restored.source == pin.source
    assert restored.pinned_at == pin.pinned_at


def test_from_dict_missing_fields_defaults():
    pin = PinnedEnv.from_dict({})
    assert pin.source == ""
    assert pin.pinned_at == ""
    assert pin.values == {}


# ---------------------------------------------------------------------------
# pin_env_file
# ---------------------------------------------------------------------------

def test_pin_env_file_reads_file(tmp_path):
    p = _write(tmp_path, ".env", """
        FOO=bar
        BAZ=qux
    """)
    pin = pin_env_file(str(p))
    assert pin.values == {"FOO": "bar", "BAZ": "qux"}
    assert os.path.isabs(pin.source)


# ---------------------------------------------------------------------------
# save / load round-trip
# ---------------------------------------------------------------------------

def test_save_and_load_pin(tmp_path):
    pin = pin_env({"K": "v"}, source="src")
    dest = str(tmp_path / "pin.json")
    save_pin(pin, dest)
    loaded = load_pin(dest)
    assert loaded.values == {"K": "v"}
    assert loaded.source == "src"


def test_save_pin_produces_valid_json(tmp_path):
    pin = pin_env({"A": "1"})
    dest = str(tmp_path / "pin.json")
    save_pin(pin, dest)
    with open(dest) as fh:
        data = json.load(fh)
    assert "values" in data and "pinned_at" in data


# ---------------------------------------------------------------------------
# diff_against_pin
# ---------------------------------------------------------------------------

def test_diff_against_pin_no_changes():
    pin = pin_env({"A": "1", "B": "2"})
    result = diff_against_pin(pin, {"A": "1", "B": "2"})
    assert not result.has_differences()


def test_diff_against_pin_detects_removed_key():
    pin = pin_env({"A": "1", "B": "2"})
    result = diff_against_pin(pin, {"A": "1"})
    assert "B" in result.missing_in_right


def test_diff_against_pin_detects_added_key():
    pin = pin_env({"A": "1"})
    result = diff_against_pin(pin, {"A": "1", "NEW": "x"})
    assert "NEW" in result.missing_in_left


def test_diff_against_pin_detects_mismatch():
    pin = pin_env({"A": "old"})
    result = diff_against_pin(pin, {"A": "new"})
    assert "A" in result.mismatched


def test_diff_file_against_pin(tmp_path):
    p = _write(tmp_path, ".env", "A=new\n")
    pin = pin_env({"A": "old"})
    result = diff_file_against_pin(pin, str(p))
    assert "A" in result.mismatched


# ---------------------------------------------------------------------------
# pin_reporter
# ---------------------------------------------------------------------------

def test_format_pin_report_no_changes():
    pin = pin_env({"A": "1"})
    result = diff_against_pin(pin, {"A": "1"})
    report = format_pin_report(pin, result, color=False)
    assert "No changes since pin" in report


def test_format_pin_report_shows_removed():
    pin = pin_env({"A": "1", "B": "2"})
    result = diff_against_pin(pin, {"A": "1"})
    report = format_pin_report(pin, result, color=False)
    assert "B" in report
    assert "removed since pin" in report


def test_format_pin_report_shows_added():
    pin = pin_env({"A": "1"})
    result = diff_against_pin(pin, {"A": "1", "NEW": "x"})
    report = format_pin_report(pin, result, color=False)
    assert "NEW" in report
    assert "added since pin" in report


def test_format_pin_report_shows_mismatch():
    pin = pin_env({"A": "old"})
    result = diff_against_pin(pin, {"A": "new"})
    report = format_pin_report(pin, result, color=False)
    assert "A" in report
    assert "old" in report
    assert "new" in report


def test_print_pin_report_writes_to_stream():
    pin = pin_env({"A": "1"})
    result = diff_against_pin(pin, {"A": "1"})
    buf = StringIO()
    print_pin_report(pin, result, color=False, file=buf)
    assert "No changes since pin" in buf.getvalue()
