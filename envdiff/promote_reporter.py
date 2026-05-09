"""Reporter for PromoteResult."""
from __future__ import annotations

from envdiff.promoter import PromoteResult

_RESET = "\033[0m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"
_BOLD = "\033[1m"


def _colorize(text: str, code: str, *, color: bool) -> str:
    return f"{code}{text}{_RESET}" if color else text


def format_promote_report(
    result: PromoteResult,
    *,
    filename: str = "",
    color: bool = True,
) -> str:
    label = filename or f"{result.source_path} -> {result.target_path}"
    lines: list[str] = []
    lines.append(_colorize(f"[promote] {label}", _BOLD, color=color))
    lines.append(_colorize(f"  Summary: {result.summary()}", _CYAN, color=color))

    if result.promoted:
        lines.append(_colorize("  Promoted (new keys):", _GREEN, color=color))
        for key, val in sorted(result.promoted.items()):
            lines.append(f"    + {key}={val}")

    if result.overwritten:
        lines.append(_colorize("  Overwritten (existing keys):", _YELLOW, color=color))
        for key, val in sorted(result.overwritten.items()):
            lines.append(f"    ~ {key}={val}")

    if result.skipped:
        lines.append("  Skipped (already present, no overwrite):")
        for key in sorted(result.skipped):
            lines.append(f"    = {key}")

    if not result.promoted and not result.overwritten and not result.skipped:
        lines.append("  (nothing to promote)")

    return "\n".join(lines)


def print_promote_report(
    result: PromoteResult,
    *,
    filename: str = "",
    color: bool = True,
) -> None:
    print(format_promote_report(result, filename=filename, color=color))
