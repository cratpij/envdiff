"""Tests for envdiff.watcher."""

import os
import tempfile
import time
from unittest.mock import MagicMock, patch

import pytest

from envdiff.watcher import EnvWatcher, watch_env_files
from envdiff.diff import EnvDiffResult


def _write(path: str, content: str) -> None:
    with open(path, "w") as f:
        f.write(content)


@pytest.fixture
def env_files():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as l, \
         tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as r:
        l.write("KEY=value\n")
        r.write("KEY=value\n")
        left, right = l.name, r.name
    yield left, right
    os.unlink(left)
    os.unlink(right)


def test_watch_env_files_returns_watcher(env_files):
    left, right = env_files
    cb = MagicMock()
    watcher = watch_env_files(left, right, cb)
    assert isinstance(watcher, EnvWatcher)
    assert watcher.left_path == left
    assert watcher.right_path == right


def test_check_once_triggers_on_first_call(env_files):
    left, right = env_files
    cb = MagicMock()
    watcher = EnvWatcher(left, right, cb)
    changed = watcher.check_once()
    assert changed is True
    cb.assert_called_once()
    result = cb.call_args[0][0]
    assert isinstance(result, EnvDiffResult)


def test_check_once_no_change_after_first(env_files):
    left, right = env_files
    cb = MagicMock()
    watcher = EnvWatcher(left, right, cb)
    watcher.check_once()  # initial
    cb.reset_mock()
    changed = watcher.check_once()
    assert changed is False
    cb.assert_not_called()


def test_check_once_detects_file_modification(env_files):
    left, right = env_files
    cb = MagicMock()
    watcher = EnvWatcher(left, right, cb)
    watcher.check_once()  # prime mtimes
    cb.reset_mock()

    time.sleep(0.05)
    _write(left, "KEY=changed\n")
    changed = watcher.check_once()
    assert changed is True
    cb.assert_called_once()


def test_check_once_missing_file_handled(env_files):
    left, right = env_files
    cb = MagicMock()
    watcher = EnvWatcher(left, right, cb)
    watcher.check_once()  # prime
    cb.reset_mock()

    os.unlink(right)
    # _has_changed returns True since mtime changed to None
    # parse_env_file raises FileNotFoundError — watcher should propagate it
    with pytest.raises(FileNotFoundError):
        watcher.check_once()


def test_start_runs_max_iterations(env_files):
    left, right = env_files
    cb = MagicMock()
    watcher = EnvWatcher(left, right, cb, poll_interval=0.0)
    watcher.start(max_iterations=3)
    # First iteration triggers change (initial), subsequent two do not
    assert cb.call_count == 1


def test_stop_sets_running_false(env_files):
    left, right = env_files
    cb = MagicMock()
    watcher = EnvWatcher(left, right, cb)
    watcher._running = True
    watcher.stop()
    assert watcher._running is False


def test_watcher_diff_result_reflects_real_diff(env_files):
    left, right = env_files
    _write(left, "A=1\nB=2\n")
    _write(right, "A=1\nC=3\n")
    cb = MagicMock()
    watcher = EnvWatcher(left, right, cb)
    watcher.check_once()

    result = cb.call_args[0][0]
    assert isinstance(result, EnvDiffResult)
    # B is only in left, C is only in right
    left_only_keys = {entry.key for entry in result.left_only}
    right_only_keys = {entry.key for entry in result.right_only}
    assert "B" in left_only_keys
    assert "C" in right_only_keys
    assert "A" not in left_only_keys
    assert "A" not in right_only_keys
