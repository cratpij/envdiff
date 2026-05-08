"""Tests for envdiff.encryptor."""

import pytest

pytest.importorskip("cryptography", reason="cryptography package required")

from envdiff.encryptor import (
    EncryptionResult,
    decrypt_env,
    encrypt_env,
    generate_key,
)


@pytest.fixture()
def key() -> str:
    return generate_key()


def test_generate_key_returns_string(key):
    assert isinstance(key, str)
    assert len(key) > 0


def test_encrypt_sensitive_keys_only(key):
    env = {"DB_PASSWORD": "secret", "APP_NAME": "myapp"}
    result = encrypt_env(env, key, sensitive_only=True)
    assert "DB_PASSWORD" in result.encrypted
    assert "APP_NAME" in result.skipped


def test_encrypt_all_keys_when_not_sensitive_only(key):
    env = {"DB_PASSWORD": "secret", "APP_NAME": "myapp"}
    result = encrypt_env(env, key, sensitive_only=False)
    assert "DB_PASSWORD" in result.encrypted
    assert "APP_NAME" in result.encrypted
    assert not result.skipped


def test_encrypt_extra_keys_included(key):
    env = {"APP_NAME": "myapp", "CUSTOM_VAR": "value"}
    result = encrypt_env(env, key, sensitive_only=True, extra_keys=["CUSTOM_VAR"])
    assert "CUSTOM_VAR" in result.encrypted
    assert "APP_NAME" in result.skipped


def test_encrypt_empty_env(key):
    result = encrypt_env({}, key)
    assert result.encrypted == {}
    assert result.skipped == []
    assert result.errors == []


def test_encrypt_then_decrypt_roundtrip(key):
    env = {"DB_PASSWORD": "supersecret", "API_KEY": "abc123"}
    enc_result = encrypt_env(env, key, sensitive_only=False)
    dec_result = decrypt_env(enc_result.encrypted, key)
    assert dec_result.encrypted == env
    assert not dec_result.errors


def test_decrypt_with_wrong_key_produces_error():
    key1 = generate_key()
    key2 = generate_key()
    env = {"SECRET": "value"}
    enc_result = encrypt_env(env, key1, sensitive_only=False)
    dec_result = decrypt_env(enc_result.encrypted, key2)
    assert dec_result.errors
    assert "SECRET" in dec_result.errors[0]


def test_encryption_result_has_no_errors(key):
    env = {"DB_PASS": "x"}
    result = encrypt_env(env, key, sensitive_only=False)
    assert not result.has_errors()


def test_encryption_result_summary_clean(key):
    env = {"DB_PASSWORD": "x", "APP_NAME": "y"}
    result = encrypt_env(env, key, sensitive_only=True)
    s = result.summary()
    assert "Encrypted" in s
    assert "skipped" in s


def test_encryption_result_summary_no_skipped(key):
    env = {"DB_PASSWORD": "x"}
    result = encrypt_env(env, key, sensitive_only=False)
    s = result.summary()
    assert "skipped" not in s


def test_source_stored_in_result(key):
    result = encrypt_env({}, key, source=".env.prod")
    assert result.source == ".env.prod"
