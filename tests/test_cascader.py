"""Tests for envdiff.cascader."""

from __future__ import annotations

import pytest

from envdiff.cascader import CascadeResult, cascade_envs, cascade_env_files


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _result(
    sources=("base.env", "override.env"),
    merged=None,
    origins=None,
    overrides=None,
) -> CascadeResult:
    return CascadeResult(
        sources=list(sources),
        merged=merged or {},
        origins=origins or {},
        overrides=overrides or {},
    )


# ---------------------------------------------------------------------------
# cascade_envs
# ---------------------------------------------------------------------------

def test_cascade_no_overlap():
    envs = [{"A": "1"}, {"B": "2"}]
    result = cascade_envs(envs, ["base", "override"])
    assert result.merged == {"A": "1", "B": "2"}


def test_cascade_later_overrides_earlier():
    envs = [{"KEY": "base_val"}, {"KEY": "new_val"}]
    result = cascade_envs(envs, ["base", "override"])
    assert result.merged["KEY"] == "new_val"
    assert result.origins["KEY"] == "override"


def test_cascade_origin_tracks_final_source():
    envs = [{"X": "1"}, {"X": "2"}, {"X": "3"}]
    result = cascade_envs(envs, ["a", "b", "c"])
    assert result.origin_of("X") == "c"


def test_cascade_was_overridden_true():
    envs = [{"FOO": "a"}, {"FOO": "b"}]
    result = cascade_envs(envs, ["s1", "s2"])
    assert result.was_overridden("FOO") is True


def test_cascade_was_overridden_false():
    envs = [{"FOO": "a"}, {"BAR": "b"}]
    result = cascade_envs(envs, ["s1", "s2"])
    assert result.was_overridden("FOO") is False


def test_cascade_mismatched_lengths_raises():
    with pytest.raises(ValueError, match="same length"):
        cascade_envs([{"A": "1"}], ["s1", "s2"])


def test_cascade_empty_inputs():
    result = cascade_envs([], [])
    assert result.merged == {}
    assert result.sources == []


def test_cascade_single_source():
    envs = [{"A": "1", "B": "2"}]
    result = cascade_envs(envs, ["only"])
    assert result.merged == {"A": "1", "B": "2"}
    assert result.origin_of("A") == "only"
    assert result.was_overridden("A") is False


# ---------------------------------------------------------------------------
# CascadeResult helpers
# ---------------------------------------------------------------------------

def test_origin_of_missing_key_returns_none():
    r = _result()
    assert r.origin_of("NONEXISTENT") is None


def test_summary_clean():
    envs = [{"A": "1"}, {"B": "2"}]
    result = cascade_envs(envs, ["base", "prod"])
    s = result.summary()
    assert "2" in s  # 2 keys
    assert "0 overridden" in s


def test_summary_with_overrides():
    envs = [{"KEY": "old"}, {"KEY": "new"}]
    result = cascade_envs(envs, ["base", "prod"])
    s = result.summary()
    assert "KEY" in s
    assert "prod" in s


# ---------------------------------------------------------------------------
# cascade_env_files (integration via tmp files)
# ---------------------------------------------------------------------------

def test_cascade_env_files(tmp_path):
    base = tmp_path / "base.env"
    base.write_text("SHARED=base\nBASE_ONLY=yes\n")
    override = tmp_path / "override.env"
    override.write_text("SHARED=overridden\nOVERRIDE_ONLY=yes\n")

    result = cascade_env_files([str(base), str(override)])

    assert result.merged["SHARED"] == "overridden"
    assert result.merged["BASE_ONLY"] == "yes"
    assert result.merged["OVERRIDE_ONLY"] == "yes"
    assert result.was_overridden("SHARED") is True
    assert result.was_overridden("BASE_ONLY") is False
