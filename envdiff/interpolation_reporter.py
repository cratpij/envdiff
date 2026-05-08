"""Format and print interpolation reports."""

from __future__ import annotations

import sys
from typing import Optional

from envdiff.interpolator import InterpolationResult


def _colorize(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_interpolation_report(
    result: InterpolationResult,
    filename: Optional[str] = None,
) -> str:
    lines = []
    header = f"Interpolation report"
    if filename:
        header += f" — {filename}"
    lines.append(_colorize(header, "1"))
    lines.append("")

    if result.cycles:
        lines.append(_colorize("  Cycles detected:", "33"))
        for key in result.cycles:
            lines.append(f"    {_colorize('~', '33')} {key}  (self-reference or cycle)")

    if result.unresolved_keys:
        lines.append(_colorize("  Unresolved references:", "31"))
        for key in result.unresolved_keys:
            lines.append(f"    {_colorize('✗', '31')} {key}")

    if result.resolved:
        lines.append(_colorize("  Resolved keys:", "32"))
        for key, value in sorted(result.resolved.items()):
            lines.append(f"    {_colorize('✓', '32')} {key} = {value}")

    lines.append("")
    status = result.summary()
    colour = "32" if result.is_clean else "31"
    lines.append(_colorize(f"  Summary: {status}", colour))
    return "\n".join(lines)


def print_interpolation_report(
    result: InterpolationResult,
    filename: Optional[str] = None,
) -> None:
    print(format_interpolation_report(result, filename), file=sys.stdout)
