"""Tests for envdiff.promoter and envdiff.promote_reporter."""
from __future__ import annotations

import pytest

from envdiff.promoter import PromoteResult, promote_envs, promoted_env, promote_env_files
from envdiff.promote_reporter import format_promote_report


SOURCE = {"DB_HOST": "staging-db", "DB_PORT": "5432", "NEW_KEY": "hello"}
TARGET = {"DB_HOST": "prod-db", "APP_ENV": "production"}


def test_promote_envs_adds_missing_keys():
    result = promote_envs(SOURCE, TARGET)
    assert "DB_PORT" in result.promoted
    assert "NEW_KEY" in result.promoted


def test_promote_envs_skips_existing_by_default():
    result = promote_envs(SOURCE, TARGET)
    assert "DB_HOST" in result.skipped
    assert "DB_HOST" not in result.promoted


def test_promote_envs_overwrites_when_flag_set():
    result = promote_envs(SOURCE, TARGET, overwrite=True)
    assert "DB_HOST" in result.overwritten
    assert result.overwritten["DB_HOST"] == "staging-db"


def test_promote_envs_respects_key_filter():
    result = promote_envs(SOURCE, TARGET, keys=["NEW_KEY"])
    assert "NEW_KEY" in result.promoted
    assert "DB_PORT" not in result.promoted
    assert "DB_PORT" not in result.skipped


def test_promote_envs_ignores_keys_not_in_source():
    result = promote_envs(SOURCE, TARGET, keys=["NONEXISTENT"])
    assert not result.promoted
    assert not result.skipped
    assert not result.overwritten


def test_promoted_env_returns_merged_dict():
    merged = promoted_env(SOURCE, TARGET)
    assert merged["APP_ENV"] == "production"   # original target key preserved
    assert merged["DB_HOST"] == "prod-db"       # not overwritten by default
    assert merged["DB_PORT"] == "5432"          # promoted from source


def test_promoted_env_overwrite_replaces_value():
    merged = promoted_env(SOURCE, TARGET, overwrite=True)
    assert merged["DB_HOST"] == "staging-db"


def test_promote_result_summary_nothing():
    result = PromoteResult(source_path="a", target_path="b")
    assert result.summary() == "nothing to promote"


def test_promote_result_summary_counts():
    result = PromoteResult(
        source_path="a",
        target_path="b",
        promoted={"A": "1"},
        skipped={"B": "2"},
        overwritten={"C": "3"},
    )
    s = result.summary()
    assert "1 promoted" in s
    assert "1 overwritten" in s
    assert "1 skipped" in s


def test_promote_env_files_sets_paths(tmp_path):
    src = tmp_path / "staging.env"
    tgt = tmp_path / "prod.env"
    src.write_text("FEATURE_FLAG=true\n")
    tgt.write_text("APP_ENV=production\n")
    result = promote_env_files(str(src), str(tgt))
    assert result.source_path == str(src)
    assert result.target_path == str(tgt)
    assert "FEATURE_FLAG" in result.promoted


def test_format_promote_report_contains_summary():
    result = PromoteResult(
        source_path="staging.env",
        target_path="prod.env",
        promoted={"NEW_KEY": "val"},
    )
    report = format_promote_report(result, color=False)
    assert "1 promoted" in report
    assert "NEW_KEY=val" in report


def test_format_promote_report_shows_skipped():
    result = PromoteResult(
        source_path="s",
        target_path="t",
        skipped={"EXISTING": "old"},
    )
    report = format_promote_report(result, color=False)
    assert "EXISTING" in report
    assert "Skipped" in report


def test_format_promote_report_empty():
    result = PromoteResult(source_path="s", target_path="t")
    report = format_promote_report(result, color=False)
    assert "nothing to promote" in report


def test_format_promote_report_filename_override():
    result = PromoteResult(source_path="s", target_path="t")
    report = format_promote_report(result, filename="custom-label", color=False)
    assert "custom-label" in report
