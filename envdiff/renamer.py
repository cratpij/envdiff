"""Rename keys across an env dict or file, with optional dry-run support."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.parser import parse_env_file


@dataclass
class RenameResult:
    """Outcome of a rename operation."""

    renamed: Dict[str, str] = field(default_factory=dict)   # old_key -> new_key
    skipped: List[str] = field(default_factory=list)         # keys not found
    env: Dict[str, str] = field(default_factory=dict)        # resulting env

    def summary(self) -> str:
        parts: List[str] = []
        if self.renamed:
            parts.append(f"{len(self.renamed)} key(s) renamed")
        if self.skipped:
            parts.append(f"{len(self.skipped)} key(s) not found (skipped)")
        if not parts:
            return "No renames applied."
        return ", ".join(parts) + "."


def rename_keys(
    env: Dict[str, str],
    mapping: Dict[str, str],
    *,
    overwrite: bool = False,
) -> RenameResult:
    """Return a new env dict with keys renamed according to *mapping*.

    Args:
        env:       Source environment dictionary.
        mapping:   ``{old_key: new_key}`` pairs to apply.
        overwrite: If *True*, overwrite *new_key* when it already exists.
                   If *False* (default), the rename is skipped for that pair.

    Returns:
        A :class:`RenameResult` with the updated env and operation metadata.
    """
    result_env: Dict[str, str] = dict(env)
    renamed: Dict[str, str] = {}
    skipped: List[str] = []

    for old_key, new_key in mapping.items():
        if old_key not in result_env:
            skipped.append(old_key)
            continue
        if new_key in result_env and not overwrite:
            skipped.append(old_key)
            continue
        value = result_env.pop(old_key)
        result_env[new_key] = value
        renamed[old_key] = new_key

    return RenameResult(renamed=renamed, skipped=skipped, env=result_env)


def rename_keys_in_file(
    path: str,
    mapping: Dict[str, str],
    *,
    overwrite: bool = False,
    encoding: str = "utf-8",
) -> RenameResult:
    """Parse *path* and apply :func:`rename_keys` to its contents."""
    env = parse_env_file(path, encoding=encoding)
    return rename_keys(env, mapping, overwrite=overwrite)
