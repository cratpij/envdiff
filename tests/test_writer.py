"""Tests for envdiff.writer — file and stdout output."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.diff import EnvDiffResult
from envdiff.writer import write_export


def _empty_result() -> EnvDiffResult:
    return EnvDiffResult(missing_in_right=set(), missing_in_left=set(), mismatched={})


def _result_with_data() -> EnvDiffResult:
    """Return a non-trivial EnvDiffResult for richer output tests."""
    return EnvDiffResult(
        missing_in_right={"FOO", "BAR"},
        missing_in_left={"BAZ"},
        mismatched={"PORT": ("8080", "9090")},
    )


def test_write_export_to_stdout_json(capsys):
    write_export(_empty_result(), "json")
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "missing_in_right" in data


def test_write_export_to_stdout_csv(capsys):
    write_export(_empty_result(), "csv")
    captured = capsys.readouterr()
    assert "key,status" in captured.out


def test_write_export_to_stdout_markdown(capsys):
    write_export(_empty_result(), "markdown")
    captured = capsys.readouterr()
    assert "|" in captured.out


def test_write_export_to_file_json(tmp_path):
    out_file = tmp_path / "report.json"
    result = EnvDiffResult(
        missing_in_right={"FOO"},
        missing_in_left=set(),
        mismatched={},
    )
    write_export(result, "json", str(out_file))
    data = json.loads(out_file.read_text())
    assert "FOO" in data["missing_in_right"]


def test_write_export_to_file_creates_parent_dirs(tmp_path):
    out_file = tmp_path / "nested" / "dir" / "report.csv"
    write_export(_empty_result(), "csv", str(out_file))
    assert out_file.exists()


def test_write_export_to_file_markdown(tmp_path):
    out_file = tmp_path / "report.md"
    write_export(_empty_result(), "markdown", str(out_file))
    content = out_file.read_text()
    assert "|" in content


def test_write_export_csv_contains_all_keys(capsys):
    """All keys from the diff result should appear in the CSV output."""
    write_export(_result_with_data(), "csv")
    captured = capsys.readouterr()
    for key in ("FOO", "BAR", "BAZ", "PORT"):
        assert key in captured.out


def test_write_export_invalid_format():
    with pytest.raises(ValueError):
        write_export(_empty_result(), "xml")  # type: ignore[arg-type]
