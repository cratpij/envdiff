"""squasher.py — Squash multiple env dicts into one, tracking key origins and conflicts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.parser import parse_env_file


@dataclass
class SquashResult:
    squashed: Dict[str, str]
    origins: Dict[str, str]          # key -> source label (last writer wins)
    conflicts: Dict[str, List[str]]  # key -> list of source labels that disagreed
    sources: List[str]

    def has_conflicts(self) -> bool:
        return bool(self.conflicts)

    def conflict_count(self) -> int:
        return len(self.conflicts)

    def summary(self) -> str:
        total = len(self.squashed)
        c = self.conflict_count()
        if c == 0:
            return f"{total} key(s) squashed from {len(self.sources)} source(s), no conflicts."
        return (
            f"{total} key(s) squashed from {len(self.sources)} source(s), "
            f"{c} conflict(s) detected."
        )


def squash_envs(
    envs: List[Dict[str, str]],
    labels: Optional[List[str]] = None,
) -> SquashResult:
    """Squash a list of env dicts (last value wins). Track conflicts."""
    if labels is None:
        labels = [f"env{i}" for i in range(len(envs))]
    if len(labels) != len(envs):
        raise ValueError("labels length must match envs length")

    squashed: Dict[str, str] = {}
    origins: Dict[str, str] = {}
    seen: Dict[str, List[str]] = {}  # key -> all source labels that defined it

    for label, env in zip(labels, envs):
        for key, value in env.items():
            if key in squashed and squashed[key] != value:
                seen.setdefault(key, [origins[key]])
                seen[key].append(label)
            elif key in squashed and squashed[key] == value:
                seen.setdefault(key, [origins[key]])
                seen[key].append(label)
            else:
                seen[key] = [label]
            squashed[key] = value
            origins[key] = label

    conflicts = {
        k: v for k, v in seen.items()
        if len(set(
            env.get(k) for env in envs if k in env
        )) > 1
    }

    return SquashResult(
        squashed=squashed,
        origins=origins,
        conflicts=conflicts,
        sources=list(labels),
    )


def squash_env_files(
    paths: List[str],
    labels: Optional[List[str]] = None,
) -> SquashResult:
    """Parse env files and squash them."""
    envs = [parse_env_file(p) for p in paths]
    if labels is None:
        labels = list(paths)
    return squash_envs(envs, labels)
