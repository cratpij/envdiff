"""Tests for envdiff.labeler."""
from __future__ import annotations

import pytest

from envdiff.labeler import LabelResult, label_env, label_env_file


@pytest.fixture()
def _env() -> dict:
    return {
        "DB_HOST": "localhost",
        "DB_PASSWORD": "secret",
        "AWS_ACCESS_KEY_ID": "AKIA123",
        "APP_DEBUG": "true",
        "PORT": "8080",
    }


_rules = [
    ("DB_*", "database"),
    ("AWS_*", "cloud"),
    ("*PASSWORD*", "sensitive"),
    ("*SECRET*", "sensitive"),
    ("*KEY*", "sensitive"),
]


def test_label_env_assigns_single_label(_env):
    result = label_env(_env, _rules)
    assert "database" in result.labels_for("DB_HOST")


def test_label_env_assigns_multiple_labels(_env):
    result = label_env(_env, _rules)
    lbls = result.labels_for("DB_PASSWORD")
    assert "database" in lbls
    assert "sensitive" in lbls


def test_label_env_unlabeled_key(_env):
    result = label_env(_env, _rules)
    assert result.labels_for("PORT") == []
    assert "PORT" in result.unlabeled_keys()


def test_label_env_keys_with_label(_env):
    result = label_env(_env, _rules)
    db_keys = result.keys_with_label("database")
    assert "DB_HOST" in db_keys
    assert "DB_PASSWORD" in db_keys
    assert "PORT" not in db_keys


def test_label_env_has_label(_env):
    result = label_env(_env, _rules)
    assert result.has_label("AWS_ACCESS_KEY_ID", "cloud")
    assert result.has_label("AWS_ACCESS_KEY_ID", "sensitive")
    assert not result.has_label("AWS_ACCESS_KEY_ID", "database")


def test_label_env_empty_env():
    result = label_env({}, _rules)
    assert result.labels == {}
    assert result.unlabeled_keys() == []


def test_label_env_no_rules(_env):
    result = label_env(_env, [])
    assert all(lbls == [] for lbls in result.labels.values())
    assert len(result.unlabeled_keys()) == len(_env)


def test_label_env_summary_labeled_only(_env):
    result = label_env(_env, _rules)
    s = result.summary()
    assert "labeled" in s


def test_label_env_summary_mentions_unlabeled(_env):
    result = label_env(_env, _rules)
    s = result.summary()
    assert "unlabeled" in s


def test_label_env_source_stored(_env):
    result = label_env(_env, _rules, source=".env.prod")
    assert result.source == ".env.prod"


def test_label_env_file_reads_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("DB_HOST=localhost\nPORT=8080\n")
    result = label_env_file(str(f), _rules)
    assert "DB_HOST" in result.env
    assert result.source == str(f)


def test_label_env_file_not_found():
    with pytest.raises(FileNotFoundError):
        label_env_file("/nonexistent/.env", _rules)
