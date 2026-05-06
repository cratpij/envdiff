"""Tests for envdiff.snapshotter."""

import json
import os
import pytest

from envdiff.snapshotter import (
    Snapshot,
    capture_snapshot,
    save_snapshot,
    load_snapshot,
    diff_against_snapshot,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


# ---------------------------------------------------------------------------
# Snapshot dataclass
# ---------------------------------------------------------------------------


def test_snapshot_to_dict():
    s = Snapshot(path=".env", captured_at="2024-01-01T00:00:00+00:00", values={"A": "1"})
    d = s.to_dict()
    assert d["path"] == ".env"
    assert d["values"] == {"A": "1"}
    assert "captured_at" in d


def test_snapshot_from_dict_roundtrip():
    original = Snapshot(path=".env.prod", captured_at="ts", values={"X": "y"})
    restored = Snapshot.from_dict(original.to_dict())
    assert restored.path == original.path
    assert restored.values == original.values
    assert restored.captured_at == original.captured_at


def test_snapshot_from_dict_missing_values_defaults_empty():
    s = Snapshot.from_dict({"path": "p", "captured_at": "t"})
    assert s.values == {}


# ---------------------------------------------------------------------------
# capture_snapshot
# ---------------------------------------------------------------------------


def test_capture_snapshot_reads_file(tmp_path):
    env = _write(tmp_path, ".env", "FOO=bar\nBAZ=qux\n")
    snap = capture_snapshot(env)
    assert snap.values == {"FOO": "bar", "BAZ": "qux"}
    assert snap.path == env
    assert snap.captured_at  # non-empty timestamp


def test_capture_snapshot_file_not_found():
    with pytest.raises(FileNotFoundError):
        capture_snapshot("/nonexistent/.env")


# ---------------------------------------------------------------------------
# save / load
# ---------------------------------------------------------------------------


def test_save_and_load_snapshot(tmp_path):
    snap = Snapshot(path=".env", captured_at="2024-06-01T12:00:00+00:00", values={"K": "v"})
    dest = str(tmp_path / "snap.json")
    save_snapshot(snap, dest)
    assert os.path.exists(dest)
    loaded = load_snapshot(dest)
    assert loaded.values == {"K": "v"}
    assert loaded.path == ".env"


def test_load_snapshot_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_snapshot("/no/such/snapshot.json")


# ---------------------------------------------------------------------------
# diff_against_snapshot
# ---------------------------------------------------------------------------


def test_diff_against_snapshot_no_changes(tmp_path):
    env = _write(tmp_path, ".env", "A=1\nB=2\n")
    snap = capture_snapshot(env)
    snap_file = str(tmp_path / "snap.json")
    save_snapshot(snap, snap_file)
    result, loaded_snap = diff_against_snapshot(env, snap_file)
    assert not result.has_differences()


def test_diff_against_snapshot_detects_new_key(tmp_path):
    env = _write(tmp_path, ".env", "A=1\n")
    snap = capture_snapshot(env)
    snap_file = str(tmp_path / "snap.json")
    save_snapshot(snap, snap_file)
    # Add a new key
    env_path = _write(tmp_path, ".env", "A=1\nNEW=key\n")
    result, _ = diff_against_snapshot(env_path, snap_file)
    assert "NEW" in result.missing_in_left


def test_diff_against_snapshot_detects_mismatch(tmp_path):
    env = _write(tmp_path, ".env", "A=old\n")
    snap = capture_snapshot(env)
    snap_file = str(tmp_path / "snap.json")
    save_snapshot(snap, snap_file)
    env_path = _write(tmp_path, ".env", "A=new\n")
    result, _ = diff_against_snapshot(env_path, snap_file)
    assert "A" in result.mismatched
