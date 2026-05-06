"""Tests for envdiff.redactor."""

from __future__ import annotations

import pathlib
import pytest

from envdiff.redactor import (
    REDACTED_PLACEHOLDER,
    is_sensitive,
    redact_env,
    redact_env_file,
    redact_value,
)


# ---------------------------------------------------------------------------
# is_sensitive
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("key", [
    "SECRET_KEY",
    "DB_PASSWORD",
    "GITHUB_TOKEN",
    "AWS_API_KEY",
    "PRIVATE_RSA",
    "AUTH_HEADER",
    "USER_CREDENTIAL",
    "PASSWD",
])
def test_is_sensitive_true(key):
    assert is_sensitive(key) is True


@pytest.mark.parametrize("key", [
    "APP_ENV",
    "PORT",
    "DATABASE_URL",
    "LOG_LEVEL",
    "FEATURE_FLAG",
])
def test_is_sensitive_false(key):
    assert is_sensitive(key) is False


# ---------------------------------------------------------------------------
# redact_value
# ---------------------------------------------------------------------------

def test_redact_value_sensitive_key():
    assert redact_value("SECRET_KEY", "abc123") == REDACTED_PLACEHOLDER


def test_redact_value_plain_key_unchanged():
    assert redact_value("APP_ENV", "production") == "production"


def test_redact_value_extra_keys():
    result = redact_value("MY_CUSTOM_KEY", "supersecret", extra_keys=frozenset({"MY_CUSTOM_KEY"}))
    assert result == REDACTED_PLACEHOLDER


def test_redact_value_extra_keys_does_not_affect_other_keys():
    result = redact_value("ANOTHER_KEY", "visible", extra_keys=frozenset({"MY_CUSTOM_KEY"}))
    assert result == "visible"


# ---------------------------------------------------------------------------
# redact_env
# ---------------------------------------------------------------------------

def test_redact_env_replaces_sensitive():
    env = {"SECRET_KEY": "abc", "APP_ENV": "prod", "DB_PASSWORD": "hunter2"}
    result = redact_env(env)
    assert result["SECRET_KEY"] == REDACTED_PLACEHOLDER
    assert result["DB_PASSWORD"] == REDACTED_PLACEHOLDER
    assert result["APP_ENV"] == "prod"


def test_redact_env_returns_new_dict():
    env = {"APP_ENV": "prod"}
    result = redact_env(env)
    assert result is not env


def test_redact_env_empty():
    assert redact_env({}) == {}


def test_redact_env_extra_keys():
    env = {"MY_VAR": "hidden", "OTHER": "visible"}
    result = redact_env(env, extra_keys=frozenset({"MY_VAR"}))
    assert result["MY_VAR"] == REDACTED_PLACEHOLDER
    assert result["OTHER"] == "visible"


# ---------------------------------------------------------------------------
# redact_env_file
# ---------------------------------------------------------------------------

def test_redact_env_file(tmp_path: pathlib.Path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "APP_ENV=production\n"
        "SECRET_KEY=topsecret\n"
        "PORT=8080\n"
    )
    result = redact_env_file(str(env_file))
    assert result["APP_ENV"] == "production"
    assert result["SECRET_KEY"] == REDACTED_PLACEHOLDER
    assert result["PORT"] == "8080"


def test_redact_env_file_not_found():
    with pytest.raises(FileNotFoundError):
        redact_env_file("/nonexistent/.env")
