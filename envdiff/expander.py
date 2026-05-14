"""Expand environment variable references within an env dict.

Supports both $VAR and ${VAR} syntax.  References that cannot be
resolved are left as-is and recorded in `unresolved`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.parser import parse_env_file

_REF_RE = re.compile(r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


@dataclass
class ExpansionResult:
    source: str
    expanded: Dict[str, str]
    unresolved: Dict[str, List[str]] = field(default_factory=dict)  # key -> [ref, ...]

    def is_clean(self) -> bool:
        return len(self.unresolved) == 0

    def summary(self) -> str:
        if self.is_clean():
            return f"{self.source}: all references resolved"
        keys = ", ".join(sorted(self.unresolved))
        return f"{self.source}: unresolved references in: {keys}"


def _refs_in(value: str) -> List[str]:
    """Return all variable names referenced inside *value*."""
    refs: List[str] = []
    for m in _REF_RE.finditer(value):
        refs.append(m.group(1) or m.group(2))
    return refs


def _expand_value(value: str, env: Dict[str, str]) -> tuple[str, List[str]]:
    """Expand a single value; return (expanded_value, unresolved_refs)."""
    missing: List[str] = []

    def replacer(m: re.Match) -> str:
        ref = m.group(1) or m.group(2)
        if ref in env:
            return env[ref]
        missing.append(ref)
        return m.group(0)  # leave unchanged

    expanded = _REF_RE.sub(replacer, value)
    return expanded, missing


def expand_env(env: Dict[str, str], source: str = "<dict>") -> ExpansionResult:
    """Expand all variable references in *env* using values within the same dict."""
    expanded: Dict[str, str] = {}
    unresolved: Dict[str, List[str]] = {}

    for key, value in env.items():
        new_value, missing = _expand_value(value, env)
        expanded[key] = new_value
        if missing:
            unresolved[key] = missing

    return ExpansionResult(source=source, expanded=expanded, unresolved=unresolved)


def expand_env_file(path: str) -> ExpansionResult:
    """Parse *path* and expand variable references within it."""
    env = parse_env_file(path)
    return expand_env(env, source=path)
