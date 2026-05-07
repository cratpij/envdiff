"""Tests for envdiff.formatter."""
from __future__ import annotations

import pytest

from envdiff.formatter import format_env_as_dotenv, format_env_as_export, format_env_as_ini


# ---------------------------------------------------------------------------
# format_env_as_dotenv
# ---------------------------------------------------------------------------

def test_dotenv_empty_dict():
    result = format_env_as_dotenv({})
    assert result == ""


def test_dotenv_simple_values():
    env = {"FOO": "bar", "BAZ": "qux"}
    result = format_env_as_dotenv(env)
    assert "FOO=bar" in result
    assert "BAZ=qux" in result


def test_dotenv_sorted_keys():
    env = {"ZEBRA": "1", "ALPHA": "2"}
    result = format_env_as_dotenv(env)
    lines = [l for l in result.splitlines() if l and not l.startswith("#")]
    assert lines[0].startswith("ALPHA")
    assert lines[1].startswith("ZEBRA")


def test_dotenv_empty_value_quoted():
    result = format_env_as_dotenv({"EMPTY": ""})
    assert 'EMPTY=""' in result


def test_dotenv_value_with_spaces_quoted():
    result = format_env_as_dotenv({"MSG": "hello world"})
    assert 'MSG="hello world"' in result


def test_dotenv_with_header():
    result = format_env_as_dotenv({"KEY": "val"}, header="Auto-generated")
    assert result.startswith("# Auto-generated")


def test_dotenv_header_already_commented():
    result = format_env_as_dotenv({"KEY": "val"}, header="# Already commented")
    # Should not double-comment
    assert "## " not in result


def test_dotenv_ends_with_newline():
    result = format_env_as_dotenv({"A": "1"})
    assert result.endswith("\n")


# ---------------------------------------------------------------------------
# format_env_as_export
# ---------------------------------------------------------------------------

def test_export_simple():
    result = format_env_as_export({"PORT": "8080"})
    assert 'export PORT="8080"' in result


def test_export_escapes_double_quotes():
    result = format_env_as_export({"GREETING": 'say "hi"'})
    assert 'say \\"hi\\"' in result


def test_export_sorted():
    env = {"Z": "1", "A": "2"}
    lines = [l for l in format_env_as_export(env).splitlines() if l.startswith("export")]
    assert lines[0].startswith("export A")


def test_export_with_header():
    result = format_env_as_export({"X": "y"}, header="Shell exports")
    assert "# Shell exports" in result


def test_export_ends_with_newline():
    assert format_env_as_export({"K": "v"}).endswith("\n")


# ---------------------------------------------------------------------------
# format_env_as_ini
# ---------------------------------------------------------------------------

def test_ini_default_section():
    result = format_env_as_ini({"FOO": "1"})
    assert result.startswith("[env]")


def test_ini_custom_section():
    result = format_env_as_ini({"FOO": "1"}, section="production")
    assert "[production]" in result


def test_ini_key_value_format():
    result = format_env_as_ini({"DB_HOST": "localhost"})
    assert "DB_HOST = localhost" in result


def test_ini_sorted_keys():
    result = format_env_as_ini({"Z": "1", "A": "2"})
    lines = result.splitlines()[1:]  # skip section header
    assert lines[0].startswith("A")


def test_ini_ends_with_newline():
    assert format_env_as_ini({"K": "v"}).endswith("\n")
