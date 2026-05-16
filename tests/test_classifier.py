"""Tests for envdiff.classifier."""

import pytest

from envdiff.classifier import (
    ClassificationResult,
    classify_env,
    classify_env_file,
    _match_category,
)


@pytest.fixture
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DB_PASSWORD": "secret",
        "AWS_ACCESS_KEY_ID": "AKIA123",
        "LOG_LEVEL": "INFO",
        "PORT": "8080",
        "FEATURE_DARK_MODE": "true",
        "APP_NAME": "myapp",
        "RETRY_COUNT": "3",
    }


def test_classify_env_categories_present(sample_env):
    result = classify_env(sample_env, source="test")
    assert "database" in result.categories
    assert "cloud" in result.categories
    assert "logging" in result.categories
    assert "network" in result.categories
    assert "feature_flag" in result.categories


def test_classify_env_db_keys(sample_env):
    result = classify_env(sample_env)
    db_keys = result.keys_in("database")
    assert "DB_HOST" in db_keys
    assert "DB_PASSWORD" in db_keys


def test_classify_env_uncategorized(sample_env):
    result = classify_env(sample_env)
    assert "APP_NAME" in result.uncategorized
    assert "RETRY_COUNT" in result.uncategorized


def test_classify_env_category_of(sample_env):
    result = classify_env(sample_env)
    assert result.category_of("LOG_LEVEL") == "logging"
    assert result.category_of("APP_NAME") is None
    assert result.category_of("AWS_ACCESS_KEY_ID") == "cloud"


def test_classify_env_empty():
    result = classify_env({}, source="empty")
    assert result.categories == {}
    assert result.uncategorized == []


def test_classify_env_custom_rules():
    env = {"MYAPP_HOST": "localhost", "MYAPP_PORT": "9000", "OTHER": "val"}
    rules = {"myapp": ["MYAPP_"]}
    result = classify_env(env, rules=rules)
    assert "myapp" in result.categories
    assert "MYAPP_HOST" in result.keys_in("myapp")
    assert "MYAPP_PORT" in result.keys_in("myapp")
    assert "OTHER" in result.uncategorized


def test_summary_contains_source(sample_env):
    result = classify_env(sample_env, source="prod.env")
    s = result.summary()
    assert "prod.env" in s
    assert "uncategorized" in s


def test_summary_shows_counts(sample_env):
    result = classify_env(sample_env)
    s = result.summary()
    assert "database: 2" in s


def test_match_category_case_insensitive():
    rules = {"db": ["DB_"]}
    assert _match_category("db_host", rules) == "db"
    assert _match_category("DB_HOST", rules) == "db"


def test_match_category_no_match():
    rules = {"db": ["DB_"]}
    assert _match_category("APP_NAME", rules) is None


def test_classify_env_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("AWS_REGION=us-east-1\nLOG_LEVEL=DEBUG\nAPP_ENV=production\n")
    result = classify_env_file(str(env_file))
    assert result.source == str(env_file)
    assert "cloud" in result.categories
    assert "logging" in result.categories
    assert "APP_ENV" in result.uncategorized


def test_classify_env_file_not_found():
    with pytest.raises(FileNotFoundError):
        classify_env_file("/nonexistent/path/.env")
