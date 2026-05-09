"""Tests for envdiff.inheritance_reporter."""

from __future__ import annotations

from envdiff.inheritor import InheritanceResult
from envdiff.inheritance_reporter import format_inheritance_report


def _result(**kwargs) -> InheritanceResult:
    defaults = dict(
        resolved={},
        inherited_keys=[],
        overridden_keys=[],
        child_only_keys=[],
        parent_path=None,
        child_path=None,
    )
    defaults.update(kwargs)
    return InheritanceResult(**defaults)


def test_format_includes_header():
    r = _result(child_path="dev.env")
    report = format_inheritance_report(r)
    assert "Inheritance Report" in report


def test_format_uses_filename_override():
    r = _result()
    report = format_inheritance_report(r, filename="custom.env")
    assert "custom.env" in report


def test_format_shows_parent_path():
    r = _result(parent_path="base.env")
    report = format_inheritance_report(r)
    assert "base.env" in report


def test_format_shows_inherited_keys():
    r = _result(
        resolved={"A": "1"},
        inherited_keys=["A"],
    )
    report = format_inheritance_report(r)
    assert "Inherited" in report
    assert "A" in report


def test_format_shows_overridden_keys():
    r = _result(
        resolved={"B": "child_val"},
        overridden_keys=["B"],
    )
    report = format_inheritance_report(r)
    assert "Overridden" in report
    assert "B" in report


def test_format_shows_child_only_keys():
    r = _result(
        resolved={"C": "3"},
        child_only_keys=["C"],
    )
    report = format_inheritance_report(r)
    assert "Child-only" in report
    assert "C" in report


def test_format_empty_result_shows_empty_message():
    r = _result()
    report = format_inheritance_report(r)
    assert "empty" in report.lower()


def test_format_shows_resolved_value():
    r = _result(
        resolved={"KEY": "myvalue"},
        inherited_keys=["KEY"],
    )
    report = format_inheritance_report(r)
    assert "myvalue" in report
