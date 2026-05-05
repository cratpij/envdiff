"""Tests for envdiff.validator."""

from __future__ import annotations

import textwrap
from unittest.mock import patch

import pytest

from envdiff.validator import (
    ValidationResult,
    validate_env,
    validate_env_file,
)


# ---------------------------------------------------------------------------
# ValidationResult helpers
# ---------------------------------------------------------------------------

def _make_result(**kwargs) -> ValidationResult:
    return ValidationResult(**kwargs)


def test_is_valid_no_issues():
    result = _make_result()
    assert result.is_valid is True


def test_is_valid_with_missing_required():
    result = _make_result(missing_required=["DB_HOST"])
    assert result.is_valid is False


def test_is_valid_extra_keys_only():
    """Extra keys alone do not make the result invalid."""
    result = _make_result(extra_keys=["EXTRA_KEY"])
    assert result.is_valid is True


def test_summary_all_ok():
    result = _make_result()
    assert result.summary() == "All required keys present."


def test_summary_missing_and_empty():
    result = _make_result(missing_required=["SECRET"], empty_values=["DB_PASS"])
    summary = result.summary()
    assert "SECRET" in summary
    assert "DB_PASS" in summary


# ---------------------------------------------------------------------------
# validate_env
# ---------------------------------------------------------------------------

def test_validate_env_all_present():
    env = {"HOST": "localhost", "PORT": "5432"}
    template = {"HOST": "", "PORT": ""}
    result = validate_env(env, template)
    assert result.is_valid
    assert result.missing_required == []
    assert result.extra_keys == []


def test_validate_env_missing_key():
    env = {"HOST": "localhost"}
    template = {"HOST": "", "PORT": ""}
    result = validate_env(env, template)
    assert not result.is_valid
    assert "PORT" in result.missing_required


def test_validate_env_extra_keys_allowed_by_default():
    env = {"HOST": "localhost", "EXTRA": "val"}
    template = {"HOST": ""}
    result = validate_env(env, template)
    assert result.extra_keys == []


def test_validate_env_extra_keys_flagged_when_disallowed():
    env = {"HOST": "localhost", "EXTRA": "val"}
    template = {"HOST": ""}
    result = validate_env(env, template, allow_extra=False)
    assert "EXTRA" in result.extra_keys


def test_validate_env_empty_values_flagged():
    env = {"HOST": "", "PORT": "5432"}
    template = {"HOST": "", "PORT": ""}
    result = validate_env(env, template, flag_empty=True)
    assert "HOST" in result.empty_values
    assert "PORT" not in result.empty_values


def test_validate_env_empty_values_not_flagged_when_disabled():
    env = {"HOST": "", "PORT": "5432"}
    template = {"HOST": "", "PORT": ""}
    result = validate_env(env, template, flag_empty=False)
    assert result.empty_values == []


# ---------------------------------------------------------------------------
# validate_env_file
# ---------------------------------------------------------------------------

def test_validate_env_file_delegates_to_parse(tmp_path):
    env_file = tmp_path / ".env"
    template_file = tmp_path / ".env.template"
    env_file.write_text("HOST=localhost\nPORT=5432\n")
    template_file.write_text("HOST=\nPORT=\nSECRET=\n")

    result = validate_env_file(str(env_file), str(template_file))
    assert not result.is_valid
    assert "SECRET" in result.missing_required
