"""Tests for envdiff.aliaser and envdiff.alias_reporter."""
from __future__ import annotations

import pytest

from envdiff.aliaser import (
    AliasResult,
    apply_aliases,
    resolve_alias,
)
from envdiff.alias_reporter import format_alias_report


# ---------------------------------------------------------------------------
# apply_aliases
# ---------------------------------------------------------------------------

def test_apply_aliases_renames_known_keys():
    env = {"DATABASE_URL": "postgres://localhost", "SECRET_KEY": "abc123"}
    aliases = {"DATABASE_URL": "db_url", "SECRET_KEY": "secret"}
    result = apply_aliases(env, aliases)
    assert "db_url" in result.aliased
    assert "secret" in result.aliased
    assert result.aliased["db_url"] == "postgres://localhost"


def test_apply_aliases_preserves_values():
    env = {"FOO": "bar"}
    result = apply_aliases(env, {"FOO": "foo_alias"})
    assert result.aliased["foo_alias"] == "bar"


def test_apply_aliases_unmapped_keys():
    env = {"A": "1", "B": "2"}
    result = apply_aliases(env, {"A": "alpha"})
    assert "B" in result.unmapped
    assert "alpha" in result.aliased


def test_apply_aliases_empty_env():
    result = apply_aliases({}, {"FOO": "bar"})
    assert result.aliased == {}
    assert result.unmapped == {}


def test_apply_aliases_empty_aliases():
    env = {"X": "1", "Y": "2"}
    result = apply_aliases(env, {})
    assert result.aliased == {}
    assert result.unmapped == {"X": "1", "Y": "2"}


def test_apply_aliases_alias_map_reverse():
    env = {"ORIG": "value"}
    result = apply_aliases(env, {"ORIG": "alias_name"})
    assert result.alias_map["alias_name"] == "ORIG"


# ---------------------------------------------------------------------------
# AliasResult helpers
# ---------------------------------------------------------------------------

def test_has_unmapped_true():
    result = AliasResult(unmapped={"X": "1"})
    assert result.has_unmapped() is True


def test_has_unmapped_false():
    result = AliasResult()
    assert result.has_unmapped() is False


def test_summary_all_aliased():
    result = AliasResult(aliased={"a": "1"}, unmapped={})
    assert "All keys aliased" in result.summary()


def test_summary_with_unmapped():
    result = AliasResult(aliased={"a": "1"}, unmapped={"B": "2"})
    assert "Unmapped" in result.summary()


# ---------------------------------------------------------------------------
# resolve_alias
# ---------------------------------------------------------------------------

def test_resolve_alias_found():
    result = AliasResult(alias_map={"my_alias": "ORIGINAL_KEY"})
    assert resolve_alias("my_alias", result) == "ORIGINAL_KEY"


def test_resolve_alias_not_found():
    result = AliasResult()
    assert resolve_alias("ghost", result) is None


# ---------------------------------------------------------------------------
# format_alias_report
# ---------------------------------------------------------------------------

def test_format_report_includes_header():
    result = AliasResult()
    report = format_alias_report(result, color=False)
    assert "Alias Report" in report


def test_format_report_includes_filename():
    result = AliasResult()
    report = format_alias_report(result, filename=".env.prod", color=False)
    assert ".env.prod" in report


def test_format_report_shows_aliased_key():
    env = {"DB": "localhost"}
    result = apply_aliases(env, {"DB": "database"})
    report = format_alias_report(result, color=False)
    assert "database" in report
    assert "DB" in report


def test_format_report_shows_unmapped():
    env = {"A": "1", "B": "2"}
    result = apply_aliases(env, {"A": "alpha"})
    report = format_alias_report(result, color=False)
    assert "Unmapped" in report
    assert "B" in report
