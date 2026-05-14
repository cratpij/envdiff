"""Format and print MigrationResult reports."""
from __future__ import annotations

from typing import Optional

from envdiff.migrator import MigrationResult


def _colorize(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_migration_report(
    result: MigrationResult,
    *,
    filename: Optional[str] = None,
    color: bool = True,
) -> str:
    label = filename or result.source_path
    lines: list[str] = []

    header = f"Migration Report — {label}"
    lines.append(_colorize(header, "1;36") if color else header)
    lines.append(f"  Target : {result.target_path}")

    if not result.migrated and not result.skipped:
        msg = "  No keys to migrate."
        lines.append(_colorize(msg, "33") if color else msg)
        return "\n".join(lines)

    if result.migrated:
        lines.append("  Migrated keys:")
        for new_key, value in sorted(result.migrated.items()):
            entry = f"    {new_key} = {value}"
            lines.append(_colorize(entry, "32") if color else entry)

    if result.skipped:
        lines.append("  Skipped (not found in source):")
        for old_key in sorted(result.skipped):
            entry = f"    {old_key}"
            lines.append(_colorize(entry, "33") if color else entry)

    if result.warnings:
        lines.append("  Warnings:")
        for w in result.warnings:
            entry = f"    {w}"
            lines.append(_colorize(entry, "31") if color else entry)

    return "\n".join(lines)


def print_migration_report(
    result: MigrationResult,
    *,
    filename: Optional[str] = None,
    color: bool = True,
) -> None:
    print(format_migration_report(result, filename=filename, color=color))
