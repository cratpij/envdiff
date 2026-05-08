"""Tests for envdiff.transformer."""

from envdiff.transformer import (
    TransformResult,
    transform_env,
    uppercase_keys,
    strip_values,
    remove_empty_values,
)


def _result(original, transformed, applied=None):
    return TransformResult(
        original=original,
        transformed=transformed,
        applied=applied or [],
    )


# --- TransformResult helpers ---

def test_changed_keys_detects_value_change():
    r = _result({"A": "old"}, {"A": "new"})
    assert r.changed_keys() == ["A"]


def test_changed_keys_empty_when_no_change():
    r = _result({"A": "same"}, {"A": "same"})
    assert r.changed_keys() == []


def test_added_keys():
    r = _result({"A": "1"}, {"A": "1", "B": "2"})
    assert r.added_keys() == ["B"]


def test_removed_keys():
    r = _result({"A": "1", "B": "2"}, {"A": "1"})
    assert r.removed_keys() == ["B"]


def test_summary_no_changes():
    r = _result({"A": "1"}, {"A": "1"})
    assert r.summary() == "No changes applied."


def test_summary_with_changes():
    r = _result({"A": "old", "B": "2"}, {"A": "new", "C": "3"})
    s = r.summary()
    assert "changed" in s
    assert "added" in s
    assert "removed" in s


# --- Built-in transforms ---

def test_uppercase_keys_transform():
    env = {"db_host": "localhost", "db_port": "5432"}
    result = transform_env(env, [("uppercase_keys", uppercase_keys)])
    assert "DB_HOST" in result.transformed
    assert "DB_PORT" in result.transformed
    assert "db_host" not in result.transformed


def test_strip_values_transform():
    env = {"KEY": "  value  ", "OTHER": "clean"}
    result = transform_env(env, [("strip_values", strip_values)])
    assert result.transformed["KEY"] == "value"
    assert result.transformed["OTHER"] == "clean"


def test_remove_empty_values_transform():
    env = {"A": "hello", "B": "", "C": "world"}
    result = transform_env(env, [("remove_empty", remove_empty_values)])
    assert "B" not in result.transformed
    assert "A" in result.transformed
    assert "C" in result.transformed


def test_transform_env_applies_multiple_transforms():
    env = {"db_host": "  localhost  ", "empty_key": ""}
    result = transform_env(env, [
        ("uppercase_keys", uppercase_keys),
        ("strip_values", strip_values),
        ("remove_empty", remove_empty_values),
    ])
    assert result.transformed.get("DB_HOST") == "localhost"
    assert "EMPTY_KEY" not in result.transformed
    assert len(result.applied) == 3


def test_transform_env_preserves_original():
    env = {"key": "val"}
    result = transform_env(env, [("uppercase_keys", uppercase_keys)])
    assert result.original == {"key": "val"}
    assert result.transformed == {"KEY": "val"}


def test_transform_env_empty_input():
    result = transform_env({}, [("strip_values", strip_values)])
    assert result.transformed == {}
    assert result.changed_keys() == []
    assert result.summary() == "No changes applied."
