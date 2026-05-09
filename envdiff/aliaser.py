"""aliaser.py — Map environment variable keys to human-friendly aliases."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class AliasResult:
    """Holds the aliased view of an env dict and any unmapped keys."""
    aliased: Dict[str, str] = field(default_factory=dict)
    unmapped: Dict[str, str] = field(default_factory=dict)
    alias_map: Dict[str, str] = field(default_factory=dict)  # alias -> original key

    def has_unmapped(self) -> bool:
        return bool(self.unmapped)

    def summary(self) -> str:
        lines = [f"Aliased: {len(self.aliased)} key(s)"]
        if self.unmapped:
            lines.append(f"Unmapped: {len(self.unmapped)} key(s)")
        else:
            lines.append("All keys aliased.")
        return "  ".join(lines)


def apply_aliases(
    env: Dict[str, str],
    aliases: Dict[str, str],
) -> AliasResult:
    """Return a new dict with keys renamed according to *aliases*.

    Args:
        env:     Original key→value mapping.
        aliases: Mapping of original_key → alias.

    Returns:
        AliasResult with aliased keys, unmapped keys, and the reverse map.
    """
    aliased: Dict[str, str] = {}
    unmapped: Dict[str, str] = {}
    alias_map: Dict[str, str] = {}

    for key, value in env.items():
        if key in aliases:
            new_key = aliases[key]
            aliased[new_key] = value
            alias_map[new_key] = key
        else:
            unmapped[key] = value

    return AliasResult(aliased=aliased, unmapped=unmapped, alias_map=alias_map)


def resolve_alias(
    alias: str,
    result: AliasResult,
) -> Optional[str]:
    """Return the original key for a given alias, or None if not found."""
    return result.alias_map.get(alias)


def apply_aliases_from_file(
    env_path: str,
    aliases: Dict[str, str],
) -> AliasResult:
    """Parse *env_path* and apply *aliases* to its keys."""
    from envdiff.parser import parse_env_file
    env = parse_env_file(env_path)
    return apply_aliases(env, aliases)
