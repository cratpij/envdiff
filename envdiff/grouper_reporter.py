"""Format and print GroupSummary reports."""

from __future__ import annotations

import sys
from typing import Dict, Optional

from envdiff.grouper import GroupSummary

_RESET = "\033[0m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_RED = "\033[31m"
_BOLD = "\033[1m"


def _c(text: str, code: str, color: bool) -> str:
    return f"{code}{text}{_RESET}" if color else text


def format_group_report(
    groups: Dict[str, GroupSummary],
    color: bool = True,
    title: Optional[str] = None,
) -> str:
    lines: list[str] = []

    header = title or "Env Diff — Grouped by Prefix"
    lines.append(_c(header, _BOLD, color))
    lines.append("-" * len(header))

    if not groups:
        lines.append(_c("No groups found.", _GREEN, color))
        return "\n".join(lines)

    for prefix, grp in sorted(groups.items()):
        status = _c("OK", _GREEN, color) if grp.is_clean else _c(f"{grp.issue_count} issue(s)", _RED, color)
        lines.append(f"\n[{_c(prefix, _BOLD, color)}]  {status}")

        for key in grp.missing_in_right:
            lines.append(f"  {_c('MISSING_RIGHT', _YELLOW, color)}  {key}")
        for key in grp.missing_in_left:
            lines.append(f"  {_c('MISSING_LEFT ', _YELLOW, color)}  {key}")
        for key in grp.mismatched:
            lines.append(f"  {_c('MISMATCH     ', _RED, color)}  {key}")

    return "\n".join(lines)


def print_group_report(
    groups: Dict[str, GroupSummary],
    color: bool = True,
    title: Optional[str] = None,
    file=None,
) -> None:
    if file is None:
        file = sys.stdout
    print(format_group_report(groups, color=color, title=title), file=file)
