"""Resolve variable references within .env values (e.g. FOO=${BAR})."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_REF_RE = re.compile(r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


@dataclass
class InterpolationResult:
    resolved: Dict[str, str] = field(default_factory=dict)
    unresolved_keys: List[str] = field(default_factory=list)
    cycles: List[str] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return not self.unresolved_keys and not self.cycles

    def summary(self) -> str:
        parts: List[str] = []
        if self.cycles:
            parts.append(f"{len(self.cycles)} cycle(s): {', '.join(self.cycles)}")
        if self.unresolved_keys:
            parts.append(f"{len(self.unresolved_keys)} unresolved: {', '.join(self.unresolved_keys)}")
        return "; ".join(parts) if parts else "all references resolved"


def _refs_in(value: str) -> List[str]:
    """Return all variable names referenced inside *value*."""
    return [m.group(1) or m.group(2) for m in _REF_RE.finditer(value)]


def _resolve_one(
    key: str,
    env: Dict[str, str],
    cache: Dict[str, Optional[str]],
    visiting: set,
) -> Optional[str]:
    if key in cache:
        return cache[key]
    if key not in env:
        cache[key] = None
        return None
    if key in visiting:
        return None  # cycle detected – caller records it
    visiting.add(key)
    value = env[key]
    def replacer(m: re.Match) -> str:
        ref = m.group(1) or m.group(2)
        resolved = _resolve_one(ref, env, cache, visiting)
        return resolved if resolved is not None else m.group(0)
    result = _REF_RE.sub(replacer, value)
    visiting.discard(key)
    cache[key] = result
    return result


def interpolate_env(env: Dict[str, str]) -> InterpolationResult:
    """Resolve all ``${VAR}`` / ``$VAR`` references in *env* and return an
    :class:`InterpolationResult` with the fully-resolved mapping."""
    cache: Dict[str, Optional[str]] = {}
    unresolved: List[str] = []
    cycles: List[str] = []
    resolved: Dict[str, str] = {}

    for key in env:
        refs = _refs_in(env[key])
        for ref in refs:
            if ref == key:
                cycles.append(key)
                break
        else:
            visiting: set = set()
            value = _resolve_one(key, env, cache, visiting)
            if value is None:
                unresolved.append(key)
            else:
                resolved[key] = value
            continue
        resolved[key] = env[key]  # keep original on cycle

    # include keys with no references
    for key, value in env.items():
        if key not in resolved:
            if key not in unresolved and key not in cycles:
                resolved[key] = cache.get(key) or value

    return InterpolationResult(
        resolved=resolved,
        unresolved_keys=unresolved,
        cycles=cycles,
    )
