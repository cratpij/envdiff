"""Integration tests: encrypt a real .env file and verify round-trip."""

import pathlib

import pytest

pytest.importorskip("cryptography", reason="cryptography package required")

from envdiff.encryptor import decrypt_env, encrypt_env, generate_key
from envdiff.parser import parse_env_file


@pytest.fixture()
def env_file(tmp_path: pathlib.Path) -> pathlib.Path:
    p = tmp_path / ".env"
    p.write_text(
        "DB_PASSWORD=hunter2\n"
        "API_SECRET=topsecret\n"
        "APP_NAME=myapp\n"
        "DEBUG=true\n"
    )
    return p


def test_encrypt_file_sensitive_keys_only(env_file):
    key = generate_key()
    env = parse_env_file(str(env_file))
    result = encrypt_env(env, key, sensitive_only=True, source=str(env_file))
    assert "DB_PASSWORD" in result.encrypted
    assert "API_SECRET" in result.encrypted
    assert "APP_NAME" in result.skipped
    assert "DEBUG" in result.skipped


def test_roundtrip_preserves_values(env_file):
    key = generate_key()
    env = parse_env_file(str(env_file))
    enc = encrypt_env(env, key, sensitive_only=False)
    dec = decrypt_env(enc.encrypted, key)
    assert dec.encrypted == env


def test_encrypted_values_differ_from_originals(env_file):
    key = generate_key()
    env = parse_env_file(str(env_file))
    enc = encrypt_env(env, key, sensitive_only=False)
    for k, v in enc.encrypted.items():
        assert v != env[k], f"{k} should have been encrypted"


def test_wrong_key_fails_decryption(env_file):
    key1 = generate_key()
    key2 = generate_key()
    env = parse_env_file(str(env_file))
    enc = encrypt_env(env, key1, sensitive_only=False)
    dec = decrypt_env(enc.encrypted, key2)
    assert dec.errors


def test_empty_env_file_roundtrip(tmp_path):
    p = tmp_path / ".env"
    p.write_text("")
    key = generate_key()
    env = parse_env_file(str(p))
    enc = encrypt_env(env, key, sensitive_only=False)
    dec = decrypt_env(enc.encrypted, key)
    assert dec.encrypted == {}
    assert not dec.errors
