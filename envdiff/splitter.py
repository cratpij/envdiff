"""Split an env dict into multiple sub-dicts based on key prefix rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.parser import parse_env_file


@dataclass
class SplitResult:
    """Result of splitting an env dict by prefix."""
    buckets: Dict[str, Dict[str, str]] = field(default_factory=dict)
    unmatched: Dict[str, str] = field(default_factory=dict)

    def bucket_names(self) -> List[str]:
        return sorted(self.buckets.keys())

    def total_keys(self) -> int:
        total = sum(len(v) for v in self.buckets.values())
        return total + len(self.unmatched)

    def summary(self) -> str:
        parts = [f"{name}: {len(keys)} key(s)" for name, keys in sorted(self.buckets.items())]
        if self.unmatched:
            parts.append(f"(unmatched): {len(self.unmatched)} key(s)")
        return ", ".join(parts) if parts else "No keys"


def split_env(
    env: Dict[str, str],
    prefixes: List[str],
    separator: str = "_",
    case_sensitive: bool = False,
) -> SplitResult:
    """Split *env* into buckets keyed by the first matching prefix.

    Keys that match no prefix end up in ``unmatched``.
    Matching is done on the portion before *separator*; if *case_sensitive* is
    False both key and prefix are compared in upper-case.
    """
    buckets: Dict[str, Dict[str, str]] = {p: {} for p in prefixes}
    unmatched: Dict[str, str] = {}

    normalise = (lambda s: s) if case_sensitive else str.upper
    norm_prefixes = [(normalise(p), p) for p in prefixes]

    for key, value in env.items():
        head = normalise(key.split(separator)[0])
        matched: Optional[str] = None
        for norm_p, orig_p in norm_prefixes:
            if head == norm_p:
                matched = orig_p
                break
        if matched is not None:
            buckets[matched][key] = value
        else:
            unmatched[key] = value

    return SplitResult(buckets=buckets, unmatched=unmatched)


def split_env_file(
    path: str,
    prefixes: List[str],
    separator: str = "_",
    case_sensitive: bool = False,
) -> SplitResult:
    """Parse *path* and split the resulting env dict."""
    env = parse_env_file(path)
    return split_env(env, prefixes, separator=separator, case_sensitive=case_sensitive)
