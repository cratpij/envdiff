"""Human-readable reporting for FreezeResult drift reports."""
from __future__ import annotations

import sys
from typing import Optional

from envdiff.freezer import FreezeResult


def _colorize(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_freeze_report(
    result: FreezeResult,
    filename: Optional[str] = None,
    color: bool = True,
) -> str:
    label = filename or result.path
    lines = []

    header = f"=== Freeze drift report: {label} ==="
    lines.append(_colorize(header, "1") if color else header)
    lines.append(f"Checksum: {result.checksum[:16]}...")

    if not result.has_drift:
        ok = "✔ No drift detected"
        lines.append(_colorize(ok, "32") if color else ok)
        return "\n".join(lines)

    if result.drifted_keys:
        section = "Changed keys:"
        lines.append(_colorize(section, "33") if color else section)
        for k in result.drifted_keys:
            old_val = result.frozen.get(k, "")
            line = f"  ~ {k}  (was: {old_val!r})"
            lines.append(_colorize(line, "33") if color else line)

    if result.added_keys:
        section = "Added keys (not in baseline):"
        lines.append(_colorize(section, "34") if color else section)
        for k in result.added_keys:
            line = f"  + {k}"
            lines.append(_colorize(line, "34") if color else line)

    if result.removed_keys:
        section = "Removed keys (missing from current):"
        lines.append(_colorize(section, "31") if color else section)
        for k in result.removed_keys:
            line = f"  - {k}"
            lines.append(_colorize(line, "31") if color else line)

    lines.append(result.summary())
    return "\n".join(lines)


def print_freeze_report(
    result: FreezeResult,
    filename: Optional[str] = None,
    color: bool = True,
    file=None,
) -> None:
    if file is None:
        file = sys.stdout
    print(format_freeze_report(result, filename=filename, color=color), file=file)
