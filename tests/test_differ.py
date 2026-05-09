"""Tests for envdiff.differ — sequential / pairwise diffing."""

from __future__ import annotations

import pytest

from envdiff.diff import EnvDiffResult
from envdiff.differ import (
    PairwiseDiff,
    SequentialDiffResult,
    diff_sequence,
    diff_sequence_files,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _pair(left: dict, right: dict, lname="a", rname="b") -> PairwiseDiff:
    from envdiff.diff import diff_envs
    return PairwiseDiff(left_path=lname, right_path=rname, result=diff_envs(left, right))


# ---------------------------------------------------------------------------
# PairwiseDiff
# ---------------------------------------------------------------------------

def test_pairwise_no_differences():
    p = _pair({"A": "1"}, {"A": "1"})
    assert not p.has_differences
    assert p.summary() == "no differences"


def test_pairwise_missing_in_right():
    p = _pair({"A": "1", "B": "2"}, {"A": "1"})
    assert p.has_differences
    assert "missing in right" in p.summary()


def test_pairwise_missing_in_left():
    p = _pair({"A": "1"}, {"A": "1", "B": "2"})
    assert p.has_differences
    assert "missing in left" in p.summary()


def test_pairwise_mismatched():
    p = _pair({"A": "1"}, {"A": "2"})
    assert p.has_differences
    assert "mismatched" in p.summary()


def test_pairwise_summary_counts_all_issues():
    p = _pair({"A": "1", "B": "2"}, {"A": "9", "C": "3"})
    s = p.summary()
    assert "missing in right" in s
    assert "missing in left" in s
    assert "mismatched" in s


# ---------------------------------------------------------------------------
# diff_sequence
# ---------------------------------------------------------------------------

def test_diff_sequence_two_identical():
    envs = [("dev", {"A": "1"}), ("staging", {"A": "1"})]
    result = diff_sequence(envs)
    assert result.total_pairs == 1
    assert result.is_clean
    assert "identical" in result.summary()


def test_diff_sequence_three_files():
    envs = [
        ("dev", {"A": "1", "B": "2"}),
        ("staging", {"A": "1", "B": "3"}),
        ("prod", {"A": "1", "B": "3", "C": "4"}),
    ]
    result = diff_sequence(envs)
    assert result.total_pairs == 2
    assert not result.is_clean
    dirty = result.pairs_with_differences()
    assert len(dirty) == 2  # staging vs dev (B mismatch), prod vs staging (C missing in staging)


def test_diff_sequence_all_clean():
    envs = [(str(i), {"X": "v"}) for i in range(4)]
    result = diff_sequence(envs)
    assert result.total_pairs == 3
    assert result.is_clean
    assert result.pairs_with_differences() == []


def test_diff_sequence_summary_dirty():
    envs = [("a", {"K": "1"}), ("b", {"K": "2"})]
    result = diff_sequence(envs)
    assert "1/1" in result.summary()


# ---------------------------------------------------------------------------
# diff_sequence_files
# ---------------------------------------------------------------------------

def test_diff_sequence_files_requires_two_paths(tmp_path):
    f = tmp_path / ".env"
    f.write_text("A=1\n")
    with pytest.raises(ValueError, match="At least two"):
        diff_sequence_files([str(f)])


def test_diff_sequence_files_reads_and_diffs(tmp_path):
    f1 = tmp_path / "dev.env"
    f2 = tmp_path / "prod.env"
    f1.write_text("A=1\nB=2\n")
    f2.write_text("A=1\nC=3\n")
    result = diff_sequence_files([str(f1), str(f2)])
    assert result.total_pairs == 1
    assert not result.is_clean
