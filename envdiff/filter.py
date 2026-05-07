"""Filter env diffs by key pattern, prefix, or change type."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from typing import Optional

from envdiff.diff import EnvDiffResult


@dataclass
class FilterOptions:
    """Options controlling which diff entries are retained."""

    pattern: Optional[str] = None          # fnmatch glob applied to key names
    prefix: Optional[str] = None           # key must start with this prefix
    include_missing_left: bool = True      # keys absent from left file
    include_missing_right: bool = True     # keys absent from right file
    include_mismatched: bool = True        # keys present in both but with different values


def _key_matches(key: str, options: FilterOptions) -> bool:
    """Return True if *key* passes the pattern and prefix filters."""
    if options.prefix is not None and not key.startswith(options.prefix):
        return False
    if options.pattern is not None and not fnmatch.fnmatch(key, options.pattern):
        return False
    return True


def filter_diff(result: EnvDiffResult, options: FilterOptions) -> EnvDiffResult:
    """Return a new :class:`EnvDiffResult` containing only entries that match *options*."""
    missing_left: dict[str, str] = {}
    missing_right: dict[str, str] = {}
    mismatched: dict[str, tuple[str, str]] = {}

    if options.include_missing_left:
        missing_left = {
            k: v
            for k, v in result.missing_in_left.items()
            if _key_matches(k, options)
        }

    if options.include_missing_right:
        missing_right = {
            k: v
            for k, v in result.missing_in_right.items()
            if _key_matches(k, options)
        }

    if options.include_mismatched:
        mismatched = {
            k: v
            for k, v in result.mismatched_values.items()
            if _key_matches(k, options)
        }

    return EnvDiffResult(
        missing_in_left=missing_left,
        missing_in_right=missing_right,
        mismatched_values=mismatched,
    )


def filter_by_pattern(result: EnvDiffResult, pattern: str) -> EnvDiffResult:
    """Convenience wrapper: filter diff to keys matching a glob *pattern*."""
    return filter_diff(result, FilterOptions(pattern=pattern))


def filter_by_prefix(result: EnvDiffResult, prefix: str) -> EnvDiffResult:
    """Convenience wrapper: filter diff to keys starting with *prefix*."""
    return filter_diff(result, FilterOptions(prefix=prefix))
