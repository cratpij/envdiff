"""Resolve final effective values from multiple env layers (base → override chain)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class ResolveResult:
    """Outcome of resolving layered env files."""

    resolved: Dict[str, str]
    sources: Dict[str, str]          # key -> label of the layer that won
    overridden: Dict[str, List[Tuple[str, str]]]  # key -> [(layer_label, value), ...]
    layer_labels: List[str]

    def was_overridden(self, key: str) -> bool:
        return key in self.overridden and len(self.overridden[key]) > 0

    def origin_of(self, key: str) -> Optional[str]:
        return self.sources.get(key)

    def summary(self) -> str:
        total = len(self.resolved)
        overridden_count = sum(1 for k in self.resolved if self.was_overridden(k))
        return (
            f"{total} key(s) resolved across {len(self.layer_labels)} layer(s); "
            f"{overridden_count} key(s) overridden."
        )


def resolve_envs(
    layers: List[Dict[str, str]],
    labels: Optional[List[str]] = None,
) -> ResolveResult:
    """Resolve keys from base to last layer; later layers override earlier ones."""
    if labels is None:
        labels = [f"layer{i}" for i in range(len(layers))]
    if len(labels) != len(layers):
        raise ValueError("labels length must match layers length")

    resolved: Dict[str, str] = {}
    sources: Dict[str, str] = {}
    overridden: Dict[str, List[Tuple[str, str]]] = {}

    for label, env in zip(labels, layers):
        for key, value in env.items():
            if key in resolved:
                overridden.setdefault(key, []).append((sources[key], resolved[key]))
            resolved[key] = value
            sources[key] = label

    return ResolveResult(
        resolved=resolved,
        sources=sources,
        overridden=overridden,
        layer_labels=labels,
    )


def resolve_env_files(
    paths: List[str],
    labels: Optional[List[str]] = None,
) -> ResolveResult:
    from envdiff.parser import parse_env_file

    layers = [parse_env_file(p) for p in paths]
    if labels is None:
        labels = list(paths)
    return resolve_envs(layers, labels)
