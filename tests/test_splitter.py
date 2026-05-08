"""Tests for envdiff.splitter."""
import pytest

from envdiff.splitter import SplitResult, split_env, split_env_file


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_NAME": "myapp",
        "APP_ENV": "production",
        "REDIS_URL": "redis://localhost",
        "UNRELATED": "value",
    }


# ---------------------------------------------------------------------------
# SplitResult unit tests
# ---------------------------------------------------------------------------

def test_split_result_bucket_names():
    result = SplitResult(buckets={"DB": {}, "APP": {}}, unmatched={})
    assert result.bucket_names() == ["APP", "DB"]


def test_split_result_total_keys():
    result = SplitResult(
        buckets={"DB": {"DB_HOST": "h"}, "APP": {"APP_NAME": "n"}},
        unmatched={"X": "1"},
    )
    assert result.total_keys() == 3


def test_split_result_summary_includes_all_buckets():
    result = SplitResult(
        buckets={"DB": {"DB_HOST": "h", "DB_PORT": "5432"}, "APP": {"APP_NAME": "n"}},
        unmatched={},
    )
    summary = result.summary()
    assert "APP: 1" in summary
    assert "DB: 2" in summary


def test_split_result_summary_shows_unmatched():
    result = SplitResult(buckets={"DB": {}}, unmatched={"UNRELATED": "v"})
    assert "(unmatched): 1" in result.summary()


def test_split_result_summary_empty():
    result = SplitResult()
    assert result.summary() == "No keys"


# ---------------------------------------------------------------------------
# split_env tests
# ---------------------------------------------------------------------------

def test_split_env_basic_routing():
    result = split_env(_env(), ["DB", "APP", "REDIS"])
    assert set(result.buckets["DB"]) == {"DB_HOST", "DB_PORT"}
    assert set(result.buckets["APP"]) == {"APP_NAME", "APP_ENV"}
    assert set(result.buckets["REDIS"]) == {"REDIS_URL"}
    assert result.unmatched == {"UNRELATED": "value"}


def test_split_env_unmatched_when_no_prefix_matches():
    result = split_env({"FOO_BAR": "1", "BAZ": "2"}, ["DB"])
    assert result.unmatched == {"FOO_BAR": "1", "BAZ": "2"}
    assert result.buckets["DB"] == {}


def test_split_env_case_insensitive_default():
    env = {"db_host": "localhost", "db_port": "5432"}
    result = split_env(env, ["DB"])
    assert "db_host" in result.buckets["DB"]
    assert "db_port" in result.buckets["DB"]


def test_split_env_case_sensitive_no_match():
    env = {"db_host": "localhost"}
    result = split_env(env, ["DB"], case_sensitive=True)
    assert result.buckets["DB"] == {}
    assert "db_host" in result.unmatched


def test_split_env_custom_separator():
    env = {"DB.HOST": "h", "APP.NAME": "n", "OTHER": "o"}
    result = split_env(env, ["DB", "APP"], separator=".")
    assert "DB.HOST" in result.buckets["DB"]
    assert "APP.NAME" in result.buckets["APP"]
    assert "OTHER" in result.unmatched


def test_split_env_empty_input():
    result = split_env({}, ["DB", "APP"])
    assert result.buckets == {"DB": {}, "APP": {}}
    assert result.unmatched == {}
    assert result.total_keys() == 0


# ---------------------------------------------------------------------------
# split_env_file tests
# ---------------------------------------------------------------------------

def test_split_env_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("DB_HOST=localhost\nAPP_NAME=myapp\nUNKNOWN=x\n")
    result = split_env_file(str(env_file), ["DB", "APP"])
    assert "DB_HOST" in result.buckets["DB"]
    assert "APP_NAME" in result.buckets["APP"]
    assert "UNKNOWN" in result.unmatched


def test_split_env_file_not_found():
    with pytest.raises(FileNotFoundError):
        split_env_file("/no/such/file.env", ["DB"])
