"""Tests for envdiff.squasher and envdiff.squash_reporter."""
import pytest

from envdiff.squasher import SquashResult, squash_envs, squash_env_files
from envdiff.squash_reporter import format_squash_report


# ---------------------------------------------------------------------------
# squash_envs
# ---------------------------------------------------------------------------

def test_squash_no_overlap():
    a = {"A": "1"}
    b = {"B": "2"}
    result = squash_envs([a, b], ["first", "second"])
    assert result.squashed == {"A": "1", "B": "2"}
    assert not result.has_conflicts()


def test_squash_last_value_wins():
    a = {"KEY": "old"}
    b = {"KEY": "new"}
    result = squash_envs([a, b], ["base", "override"])
    assert result.squashed["KEY"] == "new"
    assert result.origins["KEY"] == "override"


def test_squash_conflict_detected():
    a = {"KEY": "alpha"}
    b = {"KEY": "beta"}
    result = squash_envs([a, b], ["src1", "src2"])
    assert result.has_conflicts()
    assert "KEY" in result.conflicts


def test_squash_same_value_no_conflict():
    a = {"KEY": "same"}
    b = {"KEY": "same"}
    result = squash_envs([a, b], ["s1", "s2"])
    assert not result.has_conflicts()


def test_squash_three_sources_conflict():
    envs = [{"X": "1"}, {"X": "2"}, {"X": "3"}]
    result = squash_envs(envs, ["a", "b", "c"])
    assert result.squashed["X"] == "3"
    assert result.has_conflicts()


def test_squash_auto_labels():
    result = squash_envs([{"A": "1"}, {"B": "2"}])
    assert "env0" in result.sources
    assert "env1" in result.sources


def test_squash_labels_length_mismatch_raises():
    with pytest.raises(ValueError):
        squash_envs([{"A": "1"}], labels=["x", "y"])


def test_squash_summary_no_conflicts():
    result = squash_envs([{"A": "1", "B": "2"}], ["only"])
    assert "no conflicts" in result.summary().lower()


def test_squash_summary_with_conflicts():
    result = squash_envs([{"K": "a"}, {"K": "b"}], ["p", "q"])
    assert "conflict" in result.summary().lower()


def test_squash_conflict_count():
    result = squash_envs(
        [{"A": "1", "B": "x"}, {"A": "2", "B": "y"}],
        ["s1", "s2"],
    )
    assert result.conflict_count() == 2


# ---------------------------------------------------------------------------
# squash_env_files
# ---------------------------------------------------------------------------

def test_squash_env_files(tmp_path):
    f1 = tmp_path / ".env.base"
    f2 = tmp_path / ".env.prod"
    f1.write_text("DB_HOST=localhost\nDB_PORT=5432\n")
    f2.write_text("DB_HOST=prod.db\nAPI_KEY=secret\n")
    result = squash_env_files([str(f1), str(f2)])
    assert result.squashed["DB_HOST"] == "prod.db"
    assert result.squashed["DB_PORT"] == "5432"
    assert result.squashed["API_KEY"] == "secret"
    assert result.has_conflicts()


# ---------------------------------------------------------------------------
# format_squash_report
# ---------------------------------------------------------------------------

def _make_result(conflicts: bool) -> SquashResult:
    if conflicts:
        return squash_envs(
            [{"FOO": "bar"}, {"FOO": "baz", "NEW": "val"}],
            ["base", "prod"],
        )
    return squash_envs([{"A": "1"}, {"B": "2"}], ["x", "y"])


def test_format_includes_header():
    report = format_squash_report(_make_result(False), filename="test.env", use_color=False)
    assert "Squash Report" in report
    assert "test.env" in report


def test_format_no_conflicts_message():
    report = format_squash_report(_make_result(False), use_color=False)
    assert "no conflicts" in report.lower()


def test_format_shows_conflict_key():
    report = format_squash_report(_make_result(True), use_color=False)
    assert "FOO" in report


def test_format_shows_winner():
    report = format_squash_report(_make_result(True), use_color=False)
    assert "prod" in report


def test_format_shows_total_keys():
    result = _make_result(False)
    report = format_squash_report(result, use_color=False)
    assert str(len(result.squashed)) in report
