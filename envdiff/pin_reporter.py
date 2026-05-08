"""envdiff.pin_reporter — Format and print reports for pinned-env diffs."""
from __future__ import annotations

import sys
from typing import Optional

from envdiff.pinner import PinnedEnv
from envdiff.diff import EnvDiffResult


_RESET = "\033[0m"
_RED = "\033[31m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_BOLD = "\033[1m"


def _colorize(text: str, code: str, *, color: bool = True) -> str:
    if not color:
        return text
    return f"{code}{text}{_RESET}"


def format_pin_report(
    pin: PinnedEnv,
    result: EnvDiffResult,
    current_label: str = "current",
    *,
    color: bool = True,
) -> str:
    lines: list[str] = []

    header = f"Pin diff: {pin.source}  (pinned at {pin.pinned_at})"
    lines.append(_colorize(header, _BOLD, color=color))
    lines.append("")

    if not result.has_differences():
        lines.append(_colorize("  ✓ No changes since pin.", _GREEN, color=color))
        return "\n".join(lines)

    for key in sorted(result.missing_in_right):
        lines.append(
            _colorize(f"  - {key}  (removed since pin)", _RED, color=color)
        )

    for key in sorted(result.missing_in_left):
        lines.append(
            _colorize(f"  + {key}  (added since pin)", _GREEN, color=color)
        )

    for key, (pinned_val, current_val) in sorted(result.mismatched.items()):
        lines.append(
            _colorize(f"  ~ {key}", _YELLOW, color=color)
            + f"  pinned={pinned_val!r}  {current_label}={current_val!r}"
        )

    lines.append("")
    lines.append(result.summary())
    return "\n".join(lines)


def print_pin_report(
    pin: PinnedEnv,
    result: EnvDiffResult,
    current_label: str = "current",
    *,
    color: bool = True,
    file=None,
) -> None:
    if file is None:
        file = sys.stdout
    print(format_pin_report(pin, result, current_label, color=color), file=file)
