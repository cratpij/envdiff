"""alias_reporter.py — Format and print AliasResult reports."""
from __future__ import annotations

import sys
from typing import Optional

from envdiff.aliaser import AliasResult

_RESET = "\033[0m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"
_BOLD = "\033[1m"


def _colorize(text: str, code: str, *, color: bool) -> str:
    return f"{code}{text}{_RESET}" if color else text


def format_alias_report(
    result: AliasResult,
    filename: Optional[str] = None,
    *,
    color: bool = True,
) -> str:
    """Return a formatted string report of an AliasResult."""
    lines: list[str] = []
    header = "Alias Report"
    if filename:
        header += f" — {filename}"
    lines.append(_colorize(header, _BOLD, color=color))
    lines.append("")

    if result.aliased:
        lines.append(_colorize("Aliased keys:", _CYAN, color=color))
        for alias, original in sorted(result.alias_map.items()):
            value = result.aliased[alias]
            lines.append(
                f"  {_colorize(alias, _GREEN, color=color)}"
                f" (was: {original}) = {value}"
            )
    else:
        lines.append("  No keys were aliased.")

    if result.unmapped:
        lines.append("")
        lines.append(_colorize("Unmapped keys (no alias defined):", _YELLOW, color=color))
        for key in sorted(result.unmapped):
            lines.append(f"  {key} = {result.unmapped[key]}")

    lines.append("")
    lines.append(result.summary())
    return "\n".join(lines)


def print_alias_report(
    result: AliasResult,
    filename: Optional[str] = None,
    *,
    color: bool = True,
) -> None:
    """Print the alias report to stdout."""
    print(format_alias_report(result, filename, color=color), file=sys.stdout)
