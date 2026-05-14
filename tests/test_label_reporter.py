"""Tests for envdiff.label_reporter."""
from __future__ import annotations

from envdiff.labeler import label_env
from envdiff.label_reporter import format_label_report


_rules = [
    ("DB_*", "database"),
    ("*PASSWORD*", "sensitive"),
]


def _result(**kwargs):
    env = kwargs.pop("env", {"DB_HOST": "localhost", "PORT": "8080"})
    return label_env(env, _rules, **kwargs)


def test_format_includes_header():
    report = format_label_report(_result(), color=False)
    assert "Label report" in report


def test_format_uses_filename_override():
    report = format_label_report(_result(), filename="my.env", color=False)
    assert "my.env" in report


def test_format_uses_source_when_no_filename():
    result = _result(source=".env.staging")
    report = format_label_report(result, color=False)
    assert ".env.staging" in report


def test_format_shows_labeled_key():
    report = format_label_report(_result(), color=False)
    assert "DB_HOST" in report
    assert "database" in report


def test_format_shows_unlabeled_key():
    report = format_label_report(_result(), color=False)
    assert "PORT" in report
    assert "unlabeled" in report


def test_format_shows_summary():
    report = format_label_report(_result(), color=False)
    assert "labeled" in report


def test_format_empty_env():
    result = label_env({}, _rules)
    report = format_label_report(result, color=False)
    assert "no keys" in report


def test_format_with_color_does_not_raise():
    result = _result()
    report = format_label_report(result, color=True)
    assert "DB_HOST" in report
