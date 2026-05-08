"""Tests for envdiff.interpolation_reporter."""

import pytest
from envdiff.interpolator import InterpolationResult
from envdiff.interpolation_reporter import format_interpolation_report


def _result(**kwargs) -> InterpolationResult:
    defaults = dict(resolved={}, unresolved_keys=[], cycles=[])
    defaults.update(kwargs)
    return InterpolationResult(**defaults)


def test_format_includes_header():
    r = _result(resolved={"A": "1"})
    out = format_interpolation_report(r)
    assert "Interpolation report" in out


def test_format_includes_filename():
    r = _result()
    out = format_interpolation_report(r, filename=".env.prod")
    assert ".env.prod" in out


def test_format_shows_resolved_key():
    r = _result(resolved={"BASE": "/home"})
    out = format_interpolation_report(r)
    assert "BASE" in out
    assert "/home" in out


def test_format_shows_unresolved_key():
    r = _result(unresolved_keys=["MISSING"])
    out = format_interpolation_report(r)
    assert "MISSING" in out
    assert "Unresolved" in out


def test_format_shows_cycle_key():
    r = _result(cycles=["LOOP"])
    out = format_interpolation_report(r)
    assert "LOOP" in out
    assert "Cycle" in out or "cycle" in out


def test_format_summary_clean():
    r = _result(resolved={"K": "v"})
    out = format_interpolation_report(r)
    assert "all references resolved" in out


def test_format_summary_with_issues():
    r = _result(unresolved_keys=["X"])
    out = format_interpolation_report(r)
    assert "unresolved" in out


def test_format_no_filename_no_dash():
    r = _result()
    out = format_interpolation_report(r)
    assert " — " not in out
