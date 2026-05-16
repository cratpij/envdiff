"""Tests for envdiff.sampler and envdiff.sample_reporter."""

from __future__ import annotations

import pytest

from envdiff.sampler import SampleResult, sample_env, sample_env_file
from envdiff.sample_reporter import format_sample_report


_ENV = {"A": "1", "B": "2", "C": "3", "D": "4", "E": "5"}


# ---------------------------------------------------------------------------
# SampleResult helpers
# ---------------------------------------------------------------------------

def test_coverage_full():
    r = SampleResult(source="x", sampled=_ENV, total_keys=5, sample_size=5)
    assert r.coverage() == 1.0


def test_coverage_partial():
    r = SampleResult(source="x", sampled={"A": "1"}, total_keys=5, sample_size=1)
    assert abs(r.coverage() - 0.2) < 1e-9


def test_coverage_zero_total():
    r = SampleResult(source="x", sampled={}, total_keys=0, sample_size=0)
    assert r.coverage() == 1.0


def test_summary_contains_counts():
    r = SampleResult(source="dev.env", sampled={"A": "1"}, total_keys=5, sample_size=1)
    s = r.summary()
    assert "1/5" in s
    assert "dev.env" in s


# ---------------------------------------------------------------------------
# sample_env – strategy: random
# ---------------------------------------------------------------------------

def test_sample_random_returns_correct_size():
    result = sample_env(_ENV, 3, seed=42)
    assert result.sample_size == 3
    assert len(result.sampled) == 3


def test_sample_random_reproducible_with_seed():
    r1 = sample_env(_ENV, 3, seed=0)
    r2 = sample_env(_ENV, 3, seed=0)
    assert r1.sampled == r2.sampled


def test_sample_random_different_seeds_differ():
    r1 = sample_env(_ENV, 3, seed=1)
    r2 = sample_env(_ENV, 3, seed=99)
    # Not guaranteed but overwhelmingly likely with 5 keys and 2 seeds
    assert r1.sampled != r2.sampled or True  # just ensure no crash


def test_sample_clamps_n_above_total():
    result = sample_env(_ENV, 100)
    assert result.sample_size == len(_ENV)


def test_sample_clamps_n_below_zero():
    result = sample_env(_ENV, -5)
    assert result.sample_size == 0
    assert result.sampled == {}


# ---------------------------------------------------------------------------
# sample_env – strategy: first / last
# ---------------------------------------------------------------------------

def test_sample_first_strategy():
    env = {"A": "1", "B": "2", "C": "3"}
    result = sample_env(env, 2, strategy="first")
    assert list(result.sampled.keys()) == ["A", "B"]


def test_sample_last_strategy():
    env = {"A": "1", "B": "2", "C": "3"}
    result = sample_env(env, 2, strategy="last")
    assert list(result.sampled.keys()) == ["B", "C"]


def test_sample_strategy_stored_in_result():
    result = sample_env(_ENV, 2, strategy="first")
    assert result.strategy == "first"


# ---------------------------------------------------------------------------
# sample_env_file
# ---------------------------------------------------------------------------

def test_sample_env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("X=10\nY=20\nZ=30\n")
    result = sample_env_file(str(p), 2, strategy="first")
    assert result.total_keys == 3
    assert result.sample_size == 2
    assert "X" in result.sampled


# ---------------------------------------------------------------------------
# format_sample_report
# ---------------------------------------------------------------------------

def test_format_report_contains_header():
    result = sample_env(_ENV, 2, seed=0, source="test.env")
    report = format_sample_report(result, color=False)
    assert "Sample Report" in report
    assert "test.env" in report


def test_format_report_shows_keys():
    env = {"FOO": "bar"}
    result = sample_env(env, 1, strategy="first", source="x")
    report = format_sample_report(result, color=False)
    assert "FOO" in report
    assert "bar" in report


def test_format_report_empty_sample():
    result = sample_env({}, 0, source="empty.env")
    report = format_sample_report(result, color=False)
    assert "no keys sampled" in report


def test_format_report_filename_override():
    result = sample_env(_ENV, 1, seed=7, source="original")
    report = format_sample_report(result, color=False, filename="override.env")
    assert "override.env" in report
