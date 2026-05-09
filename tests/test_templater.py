"""Tests for envdiff.templater."""

from __future__ import annotations

import pytest

from envdiff.diff import EnvDiffResult
from envdiff.templater import (
    _placeholder,
    generate_template,
    generate_template_from_diff,
)


# ---------------------------------------------------------------------------
# _placeholder
# ---------------------------------------------------------------------------

def test_placeholder_boolean_true():
    assert _placeholder("FEATURE_FLAG", "true") == "true"


def test_placeholder_boolean_false():
    assert _placeholder("ENABLED", "false") == "false"


def test_placeholder_numeric():
    assert _placeholder("PORT", "8080") == "8080"


def test_placeholder_sensitive_value():
    assert _placeholder("SECRET_KEY", "s3cr3t") == "<secret_key>"


def test_placeholder_no_value():
    assert _placeholder("DATABASE_URL") == "<database_url>"


# ---------------------------------------------------------------------------
# generate_template
# ---------------------------------------------------------------------------

def test_generate_template_keys_sorted():
    env = {"ZEBRA": "z", "APPLE": "a", "MANGO": "m"}
    output = generate_template(env)
    keys = [line.split("=")[0] for line in output.strip().splitlines()]
    assert keys == ["APPLE", "MANGO", "ZEBRA"]


def test_generate_template_placeholders_by_default():
    env = {"API_KEY": "super-secret"}
    output = generate_template(env)
    assert "API_KEY=<api_key>" in output


def test_generate_template_include_values():
    env = {"API_KEY": "super-secret"}
    output = generate_template(env, include_values=True)
    assert "API_KEY=super-secret" in output


def test_generate_template_comment_header():
    env = {"FOO": "bar"}
    output = generate_template(env, comment_header="Auto-generated template")
    assert output.startswith("# Auto-generated template")


def test_generate_template_comment_header_already_hashed():
    env = {"FOO": "bar"}
    output = generate_template(env, comment_header="# Pre-hashed comment")
    # Should not double-hash
    assert "## " not in output
    assert "# Pre-hashed comment" in output


def test_generate_template_empty_env():
    output = generate_template({})
    assert output == "\n"


def test_generate_template_ends_with_newline():
    env = {"KEY": "val"}
    output = generate_template(env)
    assert output.endswith("\n")


def test_generate_template_comment_header_followed_by_keys():
    """Ensure the comment header appears before the key definitions."""
    env = {"FOO": "bar"}
    output = generate_template(env, comment_header="My header")
    lines = output.splitlines()
    header_index = next(i for i, l in enumerate(lines) if "My header" in l)
    key_index = next(i for i, l in enumerate(lines) if l.startswith("FOO="))
    assert header_index < key_index


# ---------------------------------------------------------------------------
# generate_template_from_diff
# ---------------------------------------------------------------------------

def _make_diff_result(
    left_only=None, right_only=None, mismatched=None
) -> EnvDiffResult:
    return EnvDiffResult(
        left_only=left_only or {},
        right_only=right_only or {},
        mismatched=mismatched or {},
    )


def test_generate_template_from_diff_combines_all_keys():
    result = _make_diff_result(
        left_only={"ONLY_LEFT": "lval"},
        right_only={"ONLY_RIGHT": "rval"},
