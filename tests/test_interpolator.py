"""Tests for envdiff.interpolator."""

import pytest
from envdiff.interpolator import (
    InterpolationResult,
    _refs_in,
    interpolate_env,
)


# ---------------------------------------------------------------------------
# _refs_in
# ---------------------------------------------------------------------------

def test_refs_in_brace_syntax():
    assert _refs_in("${FOO}") == ["FOO"]


def test_refs_in_dollar_syntax():
    assert _refs_in("$BAR") == ["BAR"]


def test_refs_in_multiple():
    assert _refs_in("${A}/$B") == ["A", "B"]


def test_refs_in_no_refs():
    assert _refs_in("plain-value") == []


# ---------------------------------------------------------------------------
# interpolate_env — happy path
# ---------------------------------------------------------------------------

def test_simple_reference_resolved():
    env = {"BASE": "/home/user", "HOME": "${BASE}/app"}
    result = interpolate_env(env)
    assert result.resolved["HOME"] == "/home/user/app"
    assert result.is_clean


def test_chained_references_resolved():
    env = {"A": "hello", "B": "${A}_world", "C": "${B}!"}
    result = interpolate_env(env)
    assert result.resolved["B"] == "hello_world"
    assert result.resolved["C"] == "hello_world!"


def test_no_references_passthrough():
    env = {"KEY": "value", "OTHER": "123"}
    result = interpolate_env(env)
    assert result.resolved == {"KEY": "value", "OTHER": "123"}
    assert result.is_clean


def test_dollar_sign_syntax_resolved():
    env = {"PREFIX": "dev", "DB": "$PREFIX-db"}
    result = interpolate_env(env)
    assert result.resolved["DB"] == "dev-db"


# ---------------------------------------------------------------------------
# interpolate_env — unresolved references
# ---------------------------------------------------------------------------

def test_missing_reference_recorded_as_unresolved():
    env = {"FOO": "${MISSING}"}
    result = interpolate_env(env)
    assert "FOO" in result.unresolved_keys
    assert not result.is_clean


def test_unresolved_summary_mentions_key():
    env = {"X": "${GHOST}"}
    result = interpolate_env(env)
    assert "unresolved" in result.summary()


# ---------------------------------------------------------------------------
# interpolate_env — cycles
# ---------------------------------------------------------------------------

def test_self_reference_is_cycle():
    env = {"LOOP": "${LOOP}"}
    result = interpolate_env(env)
    assert "LOOP" in result.cycles
    assert not result.is_clean


def test_cycle_summary_mentions_cycle():
    env = {"LOOP": "${LOOP}"}
    result = interpolate_env(env)
    assert "cycle" in result.summary()


# ---------------------------------------------------------------------------
# InterpolationResult helpers
# ---------------------------------------------------------------------------

def test_is_clean_when_empty():
    r = InterpolationResult()
    assert r.is_clean


def test_summary_all_ok():
    r = InterpolationResult(resolved={"A": "1"})
    assert r.summary() == "all references resolved"


def test_summary_combined_issues():
    r = InterpolationResult(unresolved_keys=["X"], cycles=["Y"])
    s = r.summary()
    assert "cycle" in s
    assert "unresolved" in s
