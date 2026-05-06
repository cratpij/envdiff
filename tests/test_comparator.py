"""Tests for envdiff.comparator and envdiff.comparator_reporter."""

from __future__ import annotations

import io
import pytest

from envdiff.comparator import compare_envs, compare_env_files, MultiDiffResult
from envdiff.comparator_reporter import format_multi_diff_report, print_multi_diff_report


A = {"KEY1": "a", "KEY2": "shared", "COMMON": "x"}
B = {"KEY1": "b", "KEY2": "shared", "COMMON": "x"}
C = {"KEY2": "shared", "COMMON": "x", "KEY3": "only_c"}

PATHS = ["a.env", "b.env", "c.env"]


def _result(*envs, paths=None) -> MultiDiffResult:
    p = paths or [f"f{i}.env" for i in range(len(envs))]
    return compare_envs(list(envs), p)


# --- compare_envs ---

def test_all_keys_union():
    r = _result(A, B, C)
    assert r.all_keys == {"KEY1", "KEY2", "COMMON", "KEY3"}


def test_keys_present_in_all_excludes_partial():
    r = _result(A, B, C)
    # KEY1 missing in C, KEY3 missing in A and B
    assert r.keys_present_in_all() == {"KEY2", "COMMON"}


def test_keys_missing_in_any():
    r = _result(A, B, C)
    assert r.keys_missing_in_any() == {"KEY1", "KEY3"}


def test_keys_with_value_mismatch():
    r = _result(A, B, C)
    # KEY1 differs between A and B; KEY2 and COMMON are same everywhere
    assert r.keys_with_value_mismatch() == {"KEY1"}


def test_is_consistent_true():
    env = {"X": "1", "Y": "2"}
    r = _result(env, dict(env), dict(env))
    assert r.is_consistent()


def test_is_consistent_false_missing():
    r = _result({"A": "1"}, {"A": "1", "B": "2"})
    assert not r.is_consistent()


def test_is_consistent_false_mismatch():
    r = _result({"A": "1"}, {"A": "2"})
    assert not r.is_consistent()


def test_length_mismatch_raises():
    with pytest.raises(ValueError):
        compare_envs([{"A": "1"}], ["a.env", "b.env"])


def test_matrix_contains_correct_values():
    r = _result({"K": "v1"}, {"K": "v2"}, paths=["p1", "p2"])
    assert r.matrix["K"] == {"p1": "v1", "p2": "v2"}


# --- compare_env_files ---

def test_compare_env_files(tmp_path):
    f1 = tmp_path / "one.env"
    f2 = tmp_path / "two.env"
    f1.write_text("FOO=bar\nSHARED=yes\n")
    f2.write_text("BAZ=qux\nSHARED=yes\n")
    r = compare_env_files([str(f1), str(f2)])
    assert "FOO" in r.keys_missing_in_any()
    assert "BAZ" in r.keys_missing_in_any()
    assert "SHARED" in r.keys_present_in_all()


# --- reporter ---

def test_format_consistent_contains_ok():
    env = {"A": "1"}
    r = _result(env, dict(env))
    report = format_multi_diff_report(r, use_color=False)
    assert "consistent" in report.lower()


def test_format_shows_missing_key():
    r = _result({"A": "1", "B": "2"}, {"A": "1"})
    report = format_multi_diff_report(r, use_color=False)
    assert "B" in report
    assert "absent" in report


def test_format_shows_mismatched_values():
    r = _result({"X": "foo"}, {"X": "bar"}, paths=["p1.env", "p2.env"])
    report = format_multi_diff_report(r, use_color=False)
    assert "X" in report
    assert "foo" in report
    assert "bar" in report


def test_format_lists_all_paths():
    r = _result({"A": "1"}, {"A": "1"}, paths=["alpha.env", "beta.env"])
    report = format_multi_diff_report(r, use_color=False)
    assert "alpha.env" in report
    assert "beta.env" in report


def test_print_multi_diff_report_writes_to_stream():
    env = {"K": "v"}
    r = _result(env, dict(env))
    buf = io.StringIO()
    print_multi_diff_report(r, use_color=False, file=buf)
    assert len(buf.getvalue()) > 0
