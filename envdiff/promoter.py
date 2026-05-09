"""Promote env values from one environment to another (e.g. staging -> production)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.parser import parse_env_file


@dataclass
class PromoteResult:
    source_path: str
    target_path: str
    promoted: Dict[str, str] = field(default_factory=dict)
    skipped: Dict[str, str] = field(default_factory=dict)
    overwritten: Dict[str, str] = field(default_factory=dict)

    def summary(self) -> str:
        parts = []
        if self.promoted:
            parts.append(f"{len(self.promoted)} promoted")
        if self.overwritten:
            parts.append(f"{len(self.overwritten)} overwritten")
        if self.skipped:
            parts.append(f"{len(self.skipped)} skipped")
        return ", ".join(parts) if parts else "nothing to promote"


def promote_envs(
    source: Dict[str, str],
    target: Dict[str, str],
    keys: Optional[List[str]] = None,
    overwrite: bool = False,
) -> PromoteResult:
    """Promote selected (or all) keys from source into target."""
    result = PromoteResult(source_path="", target_path="")
    candidates = keys if keys is not None else list(source.keys())

    for key in candidates:
        if key not in source:
            continue
        value = source[key]
        if key in target:
            if overwrite:
                result.overwritten[key] = value
            else:
                result.skipped[key] = target[key]
        else:
            result.promoted[key] = value

    return result


def promoted_env(
    source: Dict[str, str],
    target: Dict[str, str],
    keys: Optional[List[str]] = None,
    overwrite: bool = False,
) -> Dict[str, str]:
    """Return a new env dict with promotions applied."""
    result = promote_envs(source, target, keys=keys, overwrite=overwrite)
    merged = dict(target)
    merged.update(result.promoted)
    merged.update(result.overwritten)
    return merged


def promote_env_files(
    source_path: str,
    target_path: str,
    keys: Optional[List[str]] = None,
    overwrite: bool = False,
) -> PromoteResult:
    """Promote keys from source file into target file env dicts."""
    source = parse_env_file(source_path)
    target = parse_env_file(target_path)
    result = promote_envs(source, target, keys=keys, overwrite=overwrite)
    result.source_path = source_path
    result.target_path = target_path
    return result
