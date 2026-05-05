"""Watch .env files for changes and report diffs automatically."""

import time
import os
from typing import Callable, Optional

from envdiff.parser import parse_env_file
from envdiff.diff import diff_envs, EnvDiffResult


class EnvWatcher:
    """Watch two .env files and trigger a callback when they change."""

    def __init__(
        self,
        left_path: str,
        right_path: str,
        on_change: Callable[[EnvDiffResult], None],
        poll_interval: float = 1.0,
    ) -> None:
        self.left_path = left_path
        self.right_path = right_path
        self.on_change = on_change
        self.poll_interval = poll_interval
        self._last_mtimes: dict[str, Optional[float]] = {
            left_path: None,
            right_path: None,
        }
        self._running = False

    def _get_mtime(self, path: str) -> Optional[float]:
        try:
            return os.path.getmtime(path)
        except FileNotFoundError:
            return None

    def _has_changed(self) -> bool:
        for path in (self.left_path, self.right_path):
            current = self._get_mtime(path)
            if current != self._last_mtimes[path]:
                self._last_mtimes[path] = current
                return True
        return False

    def _compute_diff(self) -> EnvDiffResult:
        left = parse_env_file(self.left_path)
        right = parse_env_file(self.right_path)
        return diff_envs(left, right)

    def check_once(self) -> bool:
        """Check for changes once. Returns True if a change was detected."""
        if self._has_changed():
            result = self._compute_diff()
            self.on_change(result)
            return True
        return False

    def start(self, max_iterations: Optional[int] = None) -> None:
        """Start the watch loop. Runs until stop() is called or max_iterations reached."""
        self._running = True
        # Force initial check by resetting mtimes
        for path in self._last_mtimes:
            self._last_mtimes[path] = None

        iterations = 0
        while self._running:
            self.check_once()
            iterations += 1
            if max_iterations is not None and iterations >= max_iterations:
                break
            time.sleep(self.poll_interval)

    def stop(self) -> None:
        """Stop the watch loop."""
        self._running = False


def watch_env_files(
    left_path: str,
    right_path: str,
    on_change: Callable[[EnvDiffResult], None],
    poll_interval: float = 1.0,
) -> EnvWatcher:
    """Convenience function to create and return an EnvWatcher."""
    return EnvWatcher(left_path, right_path, on_change, poll_interval)
