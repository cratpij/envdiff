"""Tests for envdiff.expander and envdiff.expander_reporter."""

from __future__ import annotations

import pytest

from envdiff.expander import (
    ExpansionResult,
    _refs_in,
    expand_env,
    expand_env_file,
)
from envdiff.expander_reporter import format_expansion_report


# ---------------------------------------------------------------------------
# _refs_in
# ---------------------------------------------------------------------------

def test_refs_in_brace_syntax():
    assert _refs_in("${FOO}") == ["FOO"]


def test_refs_in_dollar_syntax():
    assert _refs_in("$BAR") == ["BAR"]


def test_refs_in_multiple():
    refs = _refs_in("${A}_$B")
    assert refs == ["A", "B"]


def test_refs_in_no_refs():
    assert _refs_in("plain_value") == []


# ---------------------------------------------------------------------------
# expand_env
# ---------------------------------------------------------------------------

def test_expand_env_simple_reference():
    env = {"BASE": "/home", "PATH": "${BASE}/bin"}
    result = expand_env(env, source="test")
    assert result.expanded["PATH"] == "/home/bin"
    assert result.is_clean()


def test_expand_env_dollar_syntax():
    env = {"HOST": "localhost", "URL": "http://$HOST:8080"}
    result = expand_env(env)
    assert result.expanded["URL"] == "http://localhost:8080"


def test_expand_env_no_references():
    env = {"FOO": "bar", "BAZ": "qux"}
    result = expand_env(env)
    assert result.expanded == env
    assert result.is_clean()


def test_expand_env_unresolved_reference():
    env = {"URL": "${MISSING}/path"}
    result = expand_env(env)
    assert not result.is_clean()
    assert "URL" in result.unresolved
    assert "MISSING" in result.unresolved["URL"]
    assert result.expanded["URL"] == "${MISSING}/path"  # left unchanged


def test_expand_env_multiple_unresolved():
    env = {"X": "$A/$B"}
    result = expand_env(env)
    assert set(result.unresolved["X"]) == {"A", "B"}


def test_expand_env_summary_clean():
    result = expand_env({"A": "1"}, source="myfile")
    assert "all references resolved" in result.summary()


def test_expand_env_summary_with_issues():
    result = expand_env({"A": "${GHOST}"}, source="myfile")
    assert "A" in result.summary()


# ---------------------------------------------------------------------------
# expand_env_file
# ---------------------------------------------------------------------------

def test_expand_env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("BASE=/opt\nFULL=${BASE}/app\n")
    result = expand_env_file(str(f))
    assert result.expanded["FULL"] == "/opt/app"
    assert result.is_clean()


def test_expand_env_file_not_found():
    with pytest.raises(FileNotFoundError):
        expand_env_file("/nonexistent/.env")


# ---------------------------------------------------------------------------
# format_expansion_report
# ---------------------------------------------------------------------------

def _make_result(unresolved=None):
    env = {"A": "1", "B": "${MISSING}"} if unresolved else {"A": "1"}
    return expand_env(env, source="test.env")


def test_format_includes_header():
    result = _make_result()
    report = format_expansion_report(result, filename="my.env", use_color=False)
    assert "my.env" in report


def test_format_clean_shows_ok_message():
    result = _make_result()
    report = format_expansion_report(result, use_color=False)
    assert "All references resolved" in report


def test_format_shows_unresolved_key():
    result = _make_result(unresolved=True)
    report = format_expansion_report(result, use_color=False)
    assert "B" in report
    assert "MISSING" in report


def test_format_shows_counts():
    result = _make_result(unresolved=True)
    report = format_expansion_report(result, use_color=False)
    assert "Unresolved: 1" in report
    assert "Total: 2" in report
