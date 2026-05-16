"""Tests for envdiff.resolver."""

import pytest

from envdiff.resolver import ResolveResult, resolve_envs


def _result() -> ResolveResult:
    layers = [
        {"HOST": "localhost", "PORT": "5432", "DEBUG": "false"},
        {"HOST": "prod.example.com", "SECRET": "abc123"},
    ]
    return resolve_envs(layers, labels=["base", "prod"])


def test_resolve_later_layer_wins() -> None:
    r = _result()
    assert r.resolved["HOST"] == "prod.example.com"


def test_resolve_base_only_key_present() -> None:
    r = _result()
    assert r.resolved["PORT"] == "5432"


def test_resolve_new_key_from_override() -> None:
    r = _result()
    assert r.resolved["SECRET"] == "abc123"


def test_origin_of_overridden_key() -> None:
    r = _result()
    assert r.origin_of("HOST") == "prod"


def test_origin_of_base_only_key() -> None:
    r = _result()
    assert r.origin_of("PORT") == "base"


def test_was_overridden_true() -> None:
    r = _result()
    assert r.was_overridden("HOST") is True


def test_was_overridden_false() -> None:
    r = _result()
    assert r.was_overridden("PORT") is False


def test_overridden_history_stored() -> None:
    r = _result()
    history = r.overridden["HOST"]
    assert history == [("base", "localhost")]


def test_summary_mentions_layers() -> None:
    r = _result()
    assert "2 layer(s)" in r.summary()


def test_summary_mentions_overridden_count() -> None:
    r = _result()
    assert "1 key(s) overridden" in r.summary()


def test_no_labels_defaults_to_layer_names() -> None:
    r = resolve_envs([{"A": "1"}, {"A": "2"}])
    assert r.layer_labels == ["layer0", "layer1"]


def test_labels_length_mismatch_raises() -> None:
    with pytest.raises(ValueError, match="labels length"):
        resolve_envs([{"A": "1"}], labels=["x", "y"])


def test_empty_layers_returns_empty_result() -> None:
    r = resolve_envs([])
    assert r.resolved == {}
    assert r.sources == {}


def test_three_layers_last_wins() -> None:
    r = resolve_envs(
        [{"K": "a"}, {"K": "b"}, {"K": "c"}],
        labels=["l1", "l2", "l3"],
    )
    assert r.resolved["K"] == "c"
    assert len(r.overridden["K"]) == 2
