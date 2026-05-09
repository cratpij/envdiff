"""Tests for envdiff/masker.py."""

import pytest

from envdiff.masker import MaskResult, mask_value, mask_env, mask_env_file


# ---------------------------------------------------------------------------
# mask_value
# ---------------------------------------------------------------------------

def test_mask_value_sensitive_key_returns_mask():
    assert mask_value("SECRET_KEY", "abc123") == "***"


def test_mask_value_plain_key_unchanged():
    assert mask_value("APP_NAME", "myapp") == "myapp"


def test_mask_value_partial_shows_prefix():
    result = mask_value("API_SECRET", "abcdef", partial=True, visible_chars=2)
    assert result == "ab***"


def test_mask_value_partial_short_value_fully_masked():
    # value shorter than visible_chars — still fully masked
    result = mask_value("API_SECRET", "a", partial=True, visible_chars=2)
    assert result == "***"


def test_mask_value_custom_mask_string():
    result = mask_value("PASSWORD", "hunter2", mask="[HIDDEN]")
    assert result == "[HIDDEN]"


def test_mask_value_extra_sensitive_keys():
    result = mask_value("MY_CUSTOM_TOKEN", "value", extra_sensitive=["MY_CUSTOM_TOKEN"])
    assert result == "***"


def test_mask_value_non_sensitive_extra_keys_unchanged():
    result = mask_value("UNRELATED", "value", extra_sensitive=["OTHER_KEY"])
    assert result == "value"


# ---------------------------------------------------------------------------
# mask_env
# ---------------------------------------------------------------------------

def test_mask_env_masks_sensitive_keys():
    env = {"SECRET": "s3cr3t", "APP_NAME": "myapp"}
    result = mask_env(env, source="test")
    assert result.masked["SECRET"] == "***"
    assert result.masked["APP_NAME"] == "myapp"


def test_mask_env_count_reflects_masked_keys():
    env = {"PASSWORD": "pass", "TOKEN": "tok", "HOST": "localhost"}
    result = mask_env(env)
    assert result.mask_count == 2


def test_mask_env_has_masked_false_when_none():
    env = {"APP_NAME": "myapp", "PORT": "8080"}
    result = mask_env(env)
    assert not result.has_masked


def test_mask_env_has_masked_true_when_some():
    env = {"API_KEY": "key123"}
    result = mask_env(env)
    assert result.has_masked


def test_mask_env_summary_no_masked():
    env = {"PORT": "8080"}
    result = mask_env(env, source=".env")
    assert "no values masked" in result.summary()


def test_mask_env_summary_with_masked():
    env = {"SECRET": "s"}
    result = mask_env(env, source=".env")
    assert "1 value(s) masked" in result.summary()


def test_mask_env_empty_dict():
    result = mask_env({})
    assert result.masked == {}
    assert result.mask_count == 0


# ---------------------------------------------------------------------------
# mask_env_file
# ---------------------------------------------------------------------------

def test_mask_env_file_reads_and_masks(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("SECRET=topsecret\nAPP=myapp\n")
    result = mask_env_file(str(env_file))
    assert result.masked["SECRET"] == "***"
    assert result.masked["APP"] == "myapp"
    assert result.source == str(env_file)


def test_mask_env_file_not_found_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        mask_env_file(str(tmp_path / "missing.env"))
