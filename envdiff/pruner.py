"""Prune obsolete or unwanted keys from an env dict based on a reference set."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from envdiff.parser import parse_env_file


@dataclass
class PruneResult:
    source: str
    reference: str
    original: Dict[str, str]
    pruned: Dict[str, str]
    removed_keys: List[str] = field(default_factory=list)
    kept_keys: List[str] = field(default_factory=list)

    @property
    def total_removed(self) -> int:
        return len(self.removed_keys)

    def summary(self) -> str:
        if not self.removed_keys:
            return f"[{self.source}] No keys pruned — all keys exist in reference."
        keys = ", ".join(sorted(self.removed_keys))
        return (
            f"[{self.source}] Pruned {self.total_removed} key(s) not in "
            f"[{self.reference}]: {keys}"
        )


def prune_env(
    env: Dict[str, str],
    reference: Dict[str, str],
    *,
    extra_keys: Optional[Set[str]] = None,
    source_name: str = "<env>",
    reference_name: str = "<reference>",
) -> PruneResult:
    """Return a copy of *env* with keys absent from *reference* removed.

    Args:
        env: The environment dict to prune.
        reference: The reference dict whose keys define what is allowed.
        extra_keys: Additional keys to keep regardless of reference.
        source_name: Label used in the result summary.
        reference_name: Label used in the result summary.
    """
    allowed: Set[str] = set(reference.keys())
    if extra_keys:
        allowed |= extra_keys

    pruned: Dict[str, str] = {}
    removed: List[str] = []
    kept: List[str] = []

    for key, value in env.items():
        if key in allowed:
            pruned[key] = value
            kept.append(key)
        else:
            removed.append(key)

    return PruneResult(
        source=source_name,
        reference=reference_name,
        original=dict(env),
        pruned=pruned,
        removed_keys=sorted(removed),
        kept_keys=sorted(kept),
    )


def prune_env_files(
    source_path: str,
    reference_path: str,
    *,
    extra_keys: Optional[Set[str]] = None,
) -> PruneResult:
    """Parse both files and prune *source_path* against *reference_path*."""
    source_env = parse_env_file(source_path)
    reference_env = parse_env_file(reference_path)
    return prune_env(
        source_env,
        reference_env,
        extra_keys=extra_keys,
        source_name=source_path,
        reference_name=reference_path,
    )
