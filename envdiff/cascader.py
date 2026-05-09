"""Cascade multiple .env files in priority order, later files overriding earlier ones."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.parser import parse_env_file


@dataclass
class CascadeResult:
    """Result of cascading multiple env files together."""

    sources: List[str]  # paths in priority order (lowest to highest)
    merged: Dict[str, str] = field(default_factory=dict)
    origins: Dict[str, str] = field(default_factory=dict)  # key -> source path
    overrides: Dict[str, List[str]] = field(default_factory=dict)  # key -> list of sources that set it

    def origin_of(self, key: str) -> Optional[str]:
        """Return the source file that provided the final value for *key*."""
        return self.origins.get(key)

    def was_overridden(self, key: str) -> bool:
        """Return True if *key* was defined in more than one source."""
        return len(self.overrides.get(key, [])) > 1

    def summary(self) -> str:
        total = len(self.merged)
        overridden = sum(1 for k in self.merged if self.was_overridden(k))
        lines = [
            f"Cascaded {len(self.sources)} file(s): {total} key(s) total, {overridden} overridden.",
        ]
        for key, srcs in self.overrides.items():
            if len(srcs) > 1:
                lines.append(f"  {key}: set in {', '.join(srcs)} -> final from {self.origins[key]}")
        return "\n".join(lines)


def cascade_envs(envs: List[Dict[str, str]], sources: List[str]) -> CascadeResult:
    """Merge *envs* in order; later dicts override earlier ones.

    Args:
        envs: List of parsed env dicts, in ascending priority order.
        sources: Corresponding source labels (e.g. file paths).

    Returns:
        A :class:`CascadeResult` with the merged env and provenance info.
    """
    if len(envs) != len(sources):
        raise ValueError("envs and sources must have the same length")

    merged: Dict[str, str] = {}
    origins: Dict[str, str] = {}
    overrides: Dict[str, List[str]] = {}

    for env, source in zip(envs, sources):
        for key, value in env.items():
            overrides.setdefault(key, [])
            overrides[key].append(source)
            merged[key] = value
            origins[key] = source

    return CascadeResult(sources=list(sources), merged=merged, origins=origins, overrides=overrides)


def cascade_env_files(paths: List[str]) -> CascadeResult:
    """Parse and cascade a list of .env file paths in ascending priority order."""
    envs = [parse_env_file(p) for p in paths]
    return cascade_envs(envs, paths)
