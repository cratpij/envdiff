"""Format and print snapshot diff reports."""

from __future__ import annotations

import sys
from typing import TextIO

from envdiff.snapshotter import Snapshot
from envdiff.diff import EnvDiffResult


def _colorize(text: str, code: str) -> str:
    """Wrap text in ANSI colour codes if stdout is a TTY."""
    if not sys.stdout.isatty():
        return text
    return f"\033[{code}m{text}\033[0m"


def format_snapshot_report(result: EnvDiffResult, snapshot: Snapshot) -> str:
    """Return a human-readable snapshot diff report as a string."""
    lines: list[str] = []
    lines.append(f"Snapshot captured : {snapshot.captured_at}")
    lines.append(f"Source file       : {snapshot.path}")
    lines.append("")

    if not result.has_differences():
        lines.append(_colorize("✔ No changes since snapshot.", "32"))
        return "\n".join(lines)

    if result.missing_in_left:
        lines.append(_colorize("Keys added since snapshot:", "32"))
        for key in sorted(result.missing_in_left):
            lines.append(f"  + {key}")
        lines.append("")

    if result.missing_in_right:
        lines.append(_colorize("Keys removed since snapshot:", "31"))
        for key in sorted(result.missing_in_right):
            lines.append(f"  - {key}")
        lines.append("")

    if result.mismatched:
        lines.append(_colorize("Values changed since snapshot:", "33"))
        for key, (old, new) in sorted(result.mismatched.items()):
            lines.append(f"  ~ {key}")
            lines.append(f"      snapshot : {old}")
            lines.append(f"      current  : {new}")
        lines.append("")

    return "\n".join(lines).rstrip()


def print_snapshot_report(
    result: EnvDiffResult,
    snapshot: Snapshot,
    file: TextIO = sys.stdout,
) -> None:
    """Print a snapshot diff report to *file* (default stdout)."""
    print(format_snapshot_report(result, snapshot), file=file)
