"""Tests for envdiff.flattener."""

import pytest

from envdiff.flattener import FlattenResult, flatten_envs


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ENV_A = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "dev"}
ENV_B = {"DB_HOST": "prod-db", "SECRET": "abc123"}
ENV_C = {"CACHE_URL": "redis://localhost"}


# ---------------------------------------------------------------------------
# FlattenResult unit tests
# ---------------------------------------------------------------------------

def test_flatten_result_no_collisions_summary():
    r = FlattenResult(flat={"A": "1"}, collisions={}, sources={"A": "base"})
    assert "no collisions" in r.summary()


def test_flatten_result_with_collisions_summary():
    r = FlattenResult(flat={"A": "1"}, collisions={"A": ["base", "override"]}, sources={"A": "override"})
    assert "collision" in r.summary()


def test_flatten_result_has_collisions_false():
    r = FlattenResult(flat={}, collisions={}, sources={})
    assert not r.has_collisions()


def test_flatten_result_has_collisions_true():
    r = FlattenResult(flat={"X": "1"}, collisions={"X": ["a", "b"]}, sources={"X": "b"})
    assert r.has_collisions()


# ---------------------------------------------------------------------------
# flatten_envs — no overlap
# ---------------------------------------------------------------------------

def test_flatten_no_overlap():
    result = flatten_envs({"a": ENV_A, "c": ENV_C})
    assert "DB_HOST" in result.flat
    assert "CACHE_URL" in result.flat
    assert not result.has_collisions()


def test_flatten_no_overlap_sources():
    result = flatten_envs({"a": ENV_A, "c": ENV_C})
    assert result.sources["DB_HOST"] == "a"
    assert result.sources["CACHE_URL"] == "c"


# ---------------------------------------------------------------------------
# flatten_envs — strategy=last (default)
# ---------------------------------------------------------------------------

def test_flatten_strategy_last_wins():
    result = flatten_envs({"a": ENV_A, "b": ENV_B})
    assert result.flat["DB_HOST"] == "prod-db"
    assert result.sources["DB_HOST"] == "b"


def test_flatten_strategy_last_records_collision():
    result = flatten_envs({"a": ENV_A, "b": ENV_B})
    assert "DB_HOST" in result.collisions
    assert "a" in result.collisions["DB_HOST"]
    assert "b" in result.collisions["DB_HOST"]


# ---------------------------------------------------------------------------
# flatten_envs — strategy=first
# ---------------------------------------------------------------------------

def test_flatten_strategy_first_wins():
    result = flatten_envs({"a": ENV_A, "b": ENV_B}, strategy="first")
    assert result.flat["DB_HOST"] == "localhost"
    assert result.sources["DB_HOST"] == "a"


def test_flatten_strategy_first_still_records_collision():
    result = flatten_envs({"a": ENV_A, "b": ENV_B}, strategy="first")
    assert "DB_HOST" in result.collisions


# ---------------------------------------------------------------------------
# flatten_envs — prefix_keys
# ---------------------------------------------------------------------------

def test_flatten_prefix_keys_no_collision():
    result = flatten_envs({"a": ENV_A, "b": ENV_B}, prefix_keys=True)
    assert not result.has_collisions()
    assert "a__DB_HOST" in result.flat
    assert "b__DB_HOST" in result.flat


def test_flatten_prefix_keys_custom_separator():
    result = flatten_envs({"x": {"KEY": "val"}}, prefix_keys=True, separator=".")
    assert "x.KEY" in result.flat


# ---------------------------------------------------------------------------
# flatten_envs — empty inputs
# ---------------------------------------------------------------------------

def test_flatten_empty_envs():
    result = flatten_envs({})
    assert result.flat == {}
    assert not result.has_collisions()


def test_flatten_single_env_no_collision():
    result = flatten_envs({"only": ENV_A})
    assert len(result.flat) == len(ENV_A)
    assert not result.has_collisions()
