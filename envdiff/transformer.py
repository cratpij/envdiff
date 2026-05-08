"""Transform env dicts by applying key/value mutations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple


@dataclass
class TransformResult:
    original: Dict[str, str]
    transformed: Dict[str, str]
    applied: List[str] = field(default_factory=list)  # names of transforms applied

    def changed_keys(self) -> List[str]:
        """Return keys whose values changed after transformation."""
        return [
            k for k in self.transformed
            if self.original.get(k) != self.transformed[k]
        ]

    def added_keys(self) -> List[str]:
        """Return keys present in transformed but not in original."""
        return [k for k in self.transformed if k not in self.original]

    def removed_keys(self) -> List[str]:
        """Return keys present in original but not in transformed."""
        return [k for k in self.original if k not in self.transformed]

    def summary(self) -> str:
        changed = len(self.changed_keys())
        added = len(self.added_keys())
        removed = len(self.removed_keys())
        if changed == 0 and added == 0 and removed == 0:
            return "No changes applied."
        parts = []
        if changed:
            parts.append(f"{changed} key(s) changed")
        if added:
            parts.append(f"{added} key(s) added")
        if removed:
            parts.append(f"{removed} key(s) removed")
        return ", ".join(parts) + "."


KeyValueTransform = Callable[[str, str], Tuple[Optional[str], str]]


def uppercase_keys(key: str, value: str) -> Tuple[Optional[str], str]:
    """Transform: uppercase all keys."""
    return key.upper(), value


def strip_values(key: str, value: str) -> Tuple[Optional[str], str]:
    """Transform: strip whitespace from values."""
    return key, value.strip()


def remove_empty_values(key: str, value: str) -> Tuple[Optional[str], str]:
    """Transform: drop keys with empty values (return None key to signal removal)."""
    if value == "":
        return None, value
    return key, value


def transform_env(
    env: Dict[str, str],
    transforms: List[Tuple[str, KeyValueTransform]],
) -> TransformResult:
    """Apply a list of named transforms to an env dict."""
    result: Dict[str, str] = dict(env)
    applied_names: List[str] = []

    for name, fn in transforms:
        next_result: Dict[str, str] = {}
        for k, v in result.items():
            new_key, new_val = fn(k, v)
            if new_key is not None:
                next_result[new_key] = new_val
        result = next_result
        applied_names.append(name)

    return TransformResult(
        original=dict(env),
        transformed=result,
        applied=applied_names,
    )
