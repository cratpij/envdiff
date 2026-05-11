"""Strip keys from an env dict based on patterns, prefixes, or an explicit list."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.parser import parse_env_file


@dataclass
class StripResult:
    original: Dict[str, str]
    stripped: Dict[str, str]
    removed_keys: List[str] = field(default_factory=list)

    def total_removed(self) -> int:
        return len(self.removed_keys)

    def summary(self) -> str:
        if not self.removed_keys:
            return "No keys removed."
        keys = ", ".join(sorted(self.removed_keys))
        return f"Removed {self.total_removed()} key(s): {keys}"


def strip_keys(
    env: Dict[str, str],
    *,
    keys: Optional[List[str]] = None,
    prefix: Optional[str] = None,
    pattern: Optional[str] = None,
) -> StripResult:
    """Return a copy of *env* with matching keys removed.

    At least one of *keys*, *prefix*, or *pattern* must be provided.
    When multiple selectors are given, a key is removed if it matches ANY of them.
    """
    if keys is None and prefix is None and pattern is None:
        raise ValueError("At least one of keys, prefix, or pattern must be provided.")

    key_set = set(keys) if keys else set()

    def _should_remove(k: str) -> bool:
        if k in key_set:
            return True
        if prefix and k.startswith(prefix):
            return True
        if pattern and fnmatch.fnmatch(k, pattern):
            return True
        return False

    removed: List[str] = []
    result: Dict[str, str] = {}
    for k, v in env.items():
        if _should_remove(k):
            removed.append(k)
        else:
            result[k] = v

    return StripResult(original=dict(env), stripped=result, removed_keys=removed)


def strip_env_file(
    path: str,
    *,
    keys: Optional[List[str]] = None,
    prefix: Optional[str] = None,
    pattern: Optional[str] = None,
) -> StripResult:
    """Parse *path* then strip matching keys."""
    env = parse_env_file(path)
    return strip_keys(env, keys=keys, prefix=prefix, pattern=pattern)
