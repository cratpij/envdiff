"""Format and print deduplication reports."""

from __future__ import annotations

import sys
from typing import Optional

from envdiff.deduplicator import DeduplicationResult


def _colorize(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_dedup_report(
    result: DeduplicationResult,
    *,
    color: bool = True,
    filename: Optional[str] = None,
) -> str:
    """Return a human-readable string describing *result*."""
    lines: list[str] = []
    label = filename or result.source

    header = f"Deduplication report: {label}"
    lines.append(_colorize(header, "1") if color else header)
    lines.append("")

    if not result.has_duplicates():
        ok = "  ✓ No duplicate keys found."
        lines.append(_colorize(ok, "32") if color else ok)
        return "\n".join(lines)

    warn_header = f"  {len(result.duplicates)} duplicate key(s) detected:"
    lines.append(_colorize(warn_header, "33") if color else warn_header)

    for key in sorted(result.duplicates):
        values = result.duplicates[key]
        winning = result.deduped[key]
        key_label = _colorize(key, "33") if color else key
        win_label = _colorize(winning, "36") if color else winning
        lines.append(f"    {key_label}  ({len(values)} occurrences, keeping: {win_label})")
        for i, v in enumerate(values, 1):
            lines.append(f"      [{i}] {v!r}")

    return "\n".join(lines)


def print_dedup_report(
    result: DeduplicationResult,
    *,
    color: bool = True,
    filename: str | None = None,
) -> None:
    """Print the deduplication report to *stdout*."""
    print(format_dedup_report(result, color=color, filename=filename), file=sys.stdout)
