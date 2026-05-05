"""Tests for envdiff.annotator."""

from __future__ import annotations

import pytest

from envdiff.annotator import annotate_env, annotate_env_files
from envdiff.diff import EnvDiffResult


def _make_result(
    missing_in_right=None,
    missing_in_left=None,
    mismatched=None,
    common=None,
) -> EnvDiffResult:
    return EnvDiffResult(
        missing_in_right=missing_in_right or [],
        missing_in_left=missing_in_left or [],
        mismatched=mismatched or {},
        common=common or {},
    )


def test_annotate_ok_keys():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = _make_result(common={"HOST": "localhost", "PORT": "5432"})
    output = annotate_env(env, result, side="left")
    assert "HOST=localhost  # OK" in output
    assert "PORT=5432  # OK" in output


def test_annotate_missing_in_right():
    env = {"SECRET": "abc"}
    result = _make_result(missing_in_right=["SECRET"])
    output = annotate_env(env, result, side="left")
    assert "SECRET=abc  # MISSING IN RIGHT" in output


def test_annotate_missing_in_left_shown_as_comment():
    env = {}
    result = _make_result(missing_in_left=["NEW_KEY"])
    output = annotate_env(env, result, side="left")
    assert "# NEW_KEY=  # MISSING IN LEFT" in output


def test_annotate_mismatch():
    env = {"DB": "postgres"}
    result = _make_result(
        mismatched={"DB": ("postgres", "mysql")},
    )
    output = annotate_env(env, result, side="left")
    assert "DB=postgres  # VALUE MISMATCH" in output


def test_annotate_right_side_missing_in_right_as_comment():
    env = {}
    result = _make_result(missing_in_right=["OLD_KEY"])
    output = annotate_env(env, result, side="right")
    assert "# OLD_KEY=  # MISSING IN RIGHT" in output


def test_annotate_right_side_missing_in_left():
    env = {"NEW_KEY": "value"}
    result = _make_result(missing_in_left=["NEW_KEY"])
    output = annotate_env(env, result, side="right")
    assert "NEW_KEY=value  # MISSING IN LEFT" in output


def test_annotate_invalid_side_raises():
    with pytest.raises(ValueError, match="side must be"):
        annotate_env({}, _make_result(), side="both")


def test_annotate_empty_env_and_result():
    output = annotate_env({}, _make_result())
    assert output == ""


def test_annotate_env_files(tmp_path):
    left = tmp_path / ".env.left"
    right = tmp_path / ".env.right"
    left.write_text("HOST=localhost\nONLY_LEFT=1\n")
    right.write_text("HOST=remotehost\nONLY_RIGHT=2\n")

    output = annotate_env_files(str(left), str(right), side="left")
    assert "HOST=localhost  # VALUE MISMATCH" in output
    assert "ONLY_LEFT=1  # MISSING IN RIGHT" in output
    assert "# ONLY_RIGHT=  # MISSING IN LEFT" in output


def test_annotate_env_files_right_side(tmp_path):
    left = tmp_path / ".env.left"
    right = tmp_path / ".env.right"
    left.write_text("SHARED=same\n")
    right.write_text("SHARED=same\nEXTRA=yes\n")

    output = annotate_env_files(str(left), str(right), side="right")
    assert "SHARED=same  # OK" in output
    assert "EXTRA=yes  # MISSING IN LEFT" in output
