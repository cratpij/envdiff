"""Integration tests: label_env_file -> format_label_report."""
from __future__ import annotations

import pytest

from envdiff.labeler import label_env_file
from envdiff.label_reporter import format_label_report


@pytest.fixture()
def env_file(tmp_path):
    content = (
        "DB_HOST=db.internal\n"
        "DB_PASSWORD=s3cr3t\n"
        "AWS_ACCESS_KEY_ID=AKIA000\n"
        "APP_ENV=production\n"
        "PORT=443\n"
    )
    p = tmp_path / ".env.prod"
    p.write_text(content)
    return str(p)


_rules = [
    ("DB_*", "database"),
    ("AWS_*", "cloud"),
    ("*PASSWORD*", "sensitive"),
    ("*KEY*", "sensitive"),
]


def test_integration_all_keys_present(env_file):
    result = label_env_file(env_file, _rules)
    assert set(result.env.keys()) == {"DB_HOST", "DB_PASSWORD", "AWS_ACCESS_KEY_ID", "APP_ENV", "PORT"}


def test_integration_db_password_has_two_labels(env_file):
    result = label_env_file(env_file, _rules)
    lbls = result.labels_for("DB_PASSWORD")
    assert "database" in lbls
    assert "sensitive" in lbls


def test_integration_unlabeled_keys(env_file):
    result = label_env_file(env_file, _rules)
    unlabeled = result.unlabeled_keys()
    assert "APP_ENV" in unlabeled
    assert "PORT" in unlabeled


def test_integration_report_contains_all_keys(env_file):
    result = label_env_file(env_file, _rules)
    report = format_label_report(result, color=False)
    for key in result.env:
        assert key in report


def test_integration_report_includes_source_path(env_file):
    result = label_env_file(env_file, _rules)
    report = format_label_report(result, color=False)
    assert env_file in report
