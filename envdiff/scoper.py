"""Scope filtering: restrict env diffs to a named set of key patterns."""
from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import Dict, List, Optional

from envdiff.diff import EnvDiffResult, diff_envs
from envdiff.parser import parse_env_file


@dataclass
class Scope:
    """A named collection of key patterns."""

    name: str
    patterns: List[str] = field(default_factory=list)

    def matches(self, key: str) -> bool:
        """Return True if *key* matches any pattern in this scope."""
        return any(fnmatch(key, p) for p in self.patterns)


@dataclass
class ScopeResult:
    """Diff result restricted to a specific scope."""

    scope: Scope
    diff: EnvDiffResult
    excluded_keys: List[str] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        from envdiff.diff import has_differences
        return not has_differences(self.diff)

    def summary(self) -> str:
        lines = [f"Scope '{self.scope.name}': {len(self.scope.patterns)} pattern(s)"]
        if self.is_clean:
            lines.append("  No differences within scope.")
        else:
            if self.diff.missing_in_right:
                lines.append(f"  Missing in right: {sorted(self.diff.missing_in_right)}")
            if self.diff.missing_in_left:
                lines.append(f"  Missing in left:  {sorted(self.diff.missing_in_left)}")
            if self.diff.mismatched:
                lines.append(f"  Mismatched keys:  {sorted(self.diff.mismatched)}")
        if self.excluded_keys:
            lines.append(f"  Excluded keys: {len(self.excluded_keys)}")
        return "\n".join(lines)


def _filter_env(env: Dict[str, str], scope: Scope) -> Dict[str, str]:
    return {k: v for k, v in env.items() if scope.matches(k)}


def scope_diff(
    left: Dict[str, str],
    right: Dict[str, str],
    scope: Scope,
) -> ScopeResult:
    """Diff *left* and *right* restricted to keys matching *scope*."""
    all_keys = set(left) | set(right)
    excluded = sorted(k for k in all_keys if not scope.matches(k))
    filtered_left = _filter_env(left, scope)
    filtered_right = _filter_env(right, scope)
    result = diff_envs(filtered_left, filtered_right)
    return ScopeResult(scope=scope, diff=result, excluded_keys=excluded)


def scope_diff_files(
    left_path: str,
    right_path: str,
    scope: Scope,
) -> ScopeResult:
    """Parse two .env files and diff them within *scope*."""
    left = parse_env_file(left_path)
    right = parse_env_file(right_path)
    return scope_diff(left, right, scope)
