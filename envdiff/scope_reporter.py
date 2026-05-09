"""Human-readable reporting for ScopeResult objects."""
from __future__ import annotations

import sys
from typing import Optional

from envdiff.scoper import ScopeResult

_RESET = "\033[0m"
_GREEN = "\033[32m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"
_BOLD = "\033[1m"


def _colorize(text: str, code: str, *, color: bool = True) -> str:
    return f"{code}{text}{_RESET}" if color else text


def format_scope_report(
    result: ScopeResult,
    left_name: Optional[str] = None,
    right_name: Optional[str] = None,
    *,
    color: bool = True,
) -> str:
    left_label = left_name or "left"
    right_label = right_name or "right"
    lines: list[str] = []

    header = f"Scope: {result.scope.name!r}  |  patterns: {result.scope.patterns}"
    lines.append(_colorize(header, _BOLD, color=color))
    lines.append("-" * len(header))

    if result.is_clean:
        lines.append(_colorize("  No differences within scope.", _GREEN, color=color))
    else:
        diff = result.diff
        for key in sorted(diff.missing_in_right):
            lines.append(
                _colorize(f"  MISSING in {right_label}: ", _RED, color=color) + key
            )
        for key in sorted(diff.missing_in_left):
            lines.append(
                _colorize(f"  MISSING in {left_label}: ", _RED, color=color) + key
            )
        for key, (lv, rv) in sorted(diff.mismatched.items()):
            lines.append(
                _colorize(f"  MISMATCH: ", _YELLOW, color=color)
                + f"{key}  ({left_label}={lv!r}  {right_label}={rv!r})"
            )

    if result.excluded_keys:
        lines.append(
            _colorize(
                f"  [{len(result.excluded_keys)} key(s) outside scope not shown]",
                _CYAN,
                color=color,
            )
        )

    return "\n".join(lines)


def print_scope_report(
    result: ScopeResult,
    left_name: Optional[str] = None,
    right_name: Optional[str] = None,
    *,
    color: bool = True,
) -> None:
    print(format_scope_report(result, left_name, right_name, color=color), file=sys.stdout)
