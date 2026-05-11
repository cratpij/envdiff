"""Flatten nested env-like structures and detect key collisions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FlattenResult:
    """Result of flattening one or more env dicts into a single namespace."""

    flat: Dict[str, str] = field(default_factory=dict)
    collisions: Dict[str, List[str]] = field(default_factory=dict)  # key -> [sources]
    sources: Dict[str, str] = field(default_factory=dict)  # key -> winning source label

    def has_collisions(self) -> bool:
        return bool(self.collisions)

    def summary(self) -> str:
        total = len(self.flat)
        col = len(self.collisions)
        if col == 0:
            return f"{total} key(s) flattened, no collisions."
        return f"{total} key(s) flattened, {col} collision(s) detected."


def flatten_envs(
    envs: Dict[str, Dict[str, str]],
    strategy: str = "last",
    separator: str = "__",
    prefix_keys: bool = False,
) -> FlattenResult:
    """Flatten multiple named env dicts into one.

    Args:
        envs: Mapping of label -> env dict.
        strategy: 'first' keeps first seen value; 'last' keeps last.
        separator: Separator used when prefix_keys=True.
        prefix_keys: If True, prefix every key with its source label.

    Returns:
        FlattenResult with merged keys, collision map, and source tracking.
    """
    flat: Dict[str, str] = {}
    collisions: Dict[str, List[str]] = {}
    sources: Dict[str, str] = {}

    for label, env in envs.items():
        for raw_key, value in env.items():
            key = f"{label}{separator}{raw_key}" if prefix_keys else raw_key

            if key in flat:
                collisions.setdefault(key, [sources[key]])
                if label not in collisions[key]:
                    collisions[key].append(label)
                if strategy == "last":
                    flat[key] = value
                    sources[key] = label
            else:
                flat[key] = value
                sources[key] = label

    return FlattenResult(flat=flat, collisions=collisions, sources=sources)


def flatten_env_files(
    paths: Dict[str, str],
    strategy: str = "last",
    separator: str = "__",
    prefix_keys: bool = False,
) -> FlattenResult:
    """Load env files by label->path and flatten them."""
    from envdiff.parser import parse_env_file

    envs = {label: parse_env_file(path) for label, path in paths.items()}
    return flatten_envs(envs, strategy=strategy, separator=separator, prefix_keys=prefix_keys)
