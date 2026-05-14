"""Migrate keys between env files using a rename map and optional value transforms."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from envdiff.parser import parse_env_file


@dataclass
class MigrationResult:
    source_path: str
    target_path: str
    migrated: Dict[str, str] = field(default_factory=dict)   # new_key -> value
    skipped: List[str] = field(default_factory=list)          # old keys not found
    warnings: List[str] = field(default_factory=list)

    def summary(self) -> str:
        parts = [f"Migration: {self.source_path} -> {self.target_path}"]
        parts.append(f"  Migrated : {len(self.migrated)} key(s)")
        parts.append(f"  Skipped  : {len(self.skipped)} key(s)")
        if self.warnings:
            for w in self.warnings:
                parts.append(f"  WARNING  : {w}")
        return "\n".join(parts)

    @property
    def has_warnings(self) -> bool:
        return bool(self.warnings)


TransformFn = Callable[[str, str], str]  # (key, value) -> new_value


def migrate_envs(
    source: Dict[str, str],
    rename_map: Dict[str, str],
    *,
    transforms: Optional[Dict[str, TransformFn]] = None,
    source_path: str = "<source>",
    target_path: str = "<target>",
) -> MigrationResult:
    """Apply *rename_map* (old_key -> new_key) to *source*, yielding a MigrationResult."""
    transforms = transforms or {}
    result = MigrationResult(source_path=source_path, target_path=target_path)

    for old_key, new_key in rename_map.items():
        if old_key not in source:
            result.skipped.append(old_key)
            continue
        value = source[old_key]
        if old_key in transforms:
            try:
                value = transforms[old_key](old_key, value)
            except Exception as exc:  # noqa: BLE001
                result.warnings.append(f"Transform for '{old_key}' failed: {exc}")
        if new_key in result.migrated:
            result.warnings.append(f"Target key '{new_key}' already set; overwriting.")
        result.migrated[new_key] = value

    return result


def migrate_env_files(
    source_path: str,
    rename_map: Dict[str, str],
    *,
    transforms: Optional[Dict[str, TransformFn]] = None,
    target_path: str = "<target>",
) -> MigrationResult:
    """Convenience wrapper that parses *source_path* before migrating."""
    source = parse_env_file(source_path)
    return migrate_envs(
        source,
        rename_map,
        transforms=transforms,
        source_path=source_path,
        target_path=target_path,
    )
