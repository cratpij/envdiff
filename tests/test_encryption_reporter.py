"""Tests for envdiff.encryption_reporter."""

import pytest

pytest.importorskip("cryptography", reason="cryptography package required")

from envdiff.encryptor import EncryptionResult, encrypt_env, generate_key
from envdiff.encryption_reporter import format_encryption_report


@pytest.fixture()
def _key():
    return generate_key()


def _result(**kwargs) -> EncryptionResult:
    r = EncryptionResult(source=".env")
    for attr, val in kwargs.items():
        setattr(r, attr, val)
    return r


def test_format_includes_header():
    r = _result()
    report = format_encryption_report(r, color=False)
    assert "Encryption report" in report


def test_format_includes_filename():
    r = _result()
    report = format_encryption_report(r, color=False, filename=".env.prod")
    assert ".env.prod" in report


def test_format_shows_encrypted_keys():
    r = _result(encrypted={"DB_PASSWORD": "tok123"})
    report = format_encryption_report(r, color=False)
    assert "DB_PASSWORD" in report
    assert "Encrypted:" in report


def test_format_shows_skipped_keys():
    r = _result(skipped=["APP_NAME"])
    report = format_encryption_report(r, color=False)
    assert "APP_NAME" in report
    assert "Skipped" in report


def test_format_shows_errors():
    r = _result(errors=["SECRET: invalid token"])
    report = format_encryption_report(r, color=False)
    assert "invalid token" in report
    assert "Errors:" in report


def test_format_summary_present():
    r = _result(encrypted={"API_KEY": "tok"})
    report = format_encryption_report(r, color=False)
    assert "Encrypted 1 key" in report


def test_format_no_color_no_escape_codes():
    r = _result(encrypted={"DB_PASSWORD": "tok"})
    report = format_encryption_report(r, color=False)
    assert "\033[" not in report


def test_format_color_contains_escape_codes():
    r = _result(encrypted={"DB_PASSWORD": "tok"})
    report = format_encryption_report(r, color=True)
    assert "\033[" in report
