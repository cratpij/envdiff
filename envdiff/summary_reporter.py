"""Reporter for DiffSummaryStats — human-readable and colourised output."""

from __future__ import annotations

import sys
from typing import TextIO

from envdiff.differ_summary import DiffSummaryStats

_RESET = "\033[0m"
_GREEN = "\033[32m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_BOLD = "\033[1m"


def _c(text: str, code: str, colour: bool) -> str:
    return f"{code}{text}{_RESET}" if colour else text


def format_summary_report(stats: DiffSummaryStats, colour: bool = True) -> str:
    lines: list[str] = []

    header = _c("Diff Summary", _BOLD, colour)
    lines.append(header)
    lines.append("-" * 40)

    lines.append(f"File pairs compared : {stats.total_files}")
    lines.append(f"Keys compared       : {stats.total_keys_compared}")

    diff_label = _c(
        str(stats.files_with_differences),
        _RED if stats.files_with_differences else _GREEN,
        colour,
    )
    lines.append(f"Pairs with diffs    : {diff_label}")
    lines.append(f"Missing in right    : {stats.total_missing_in_right}")
    lines.append(f"Missing in left     : {stats.total_missing_in_left}")
    lines.append(f"Mismatched values   : {stats.total_mismatched}")
    lines.append("-" * 40)

    if stats.per_file:
        lines.append("Per-file breakdown:")
        for label, counts in stats.per_file.items():
            has_issues = any(v for v in counts.values())
            indicator = _c("✗", _RED, colour) if has_issues else _c("✓", _GREEN, colour)
            lines.append(
                f"  {indicator} {label}  "
                f"[miss-r={counts['missing_in_right']} "
                f"miss-l={counts['missing_in_left']} "
                f"mismatch={counts['mismatched']}]"
            )

    lines.append("")
    verdict = stats.summary()
    lines.append(_c(verdict, _GREEN if stats.is_clean else _YELLOW, colour))

    return "\n".join(lines)


def print_summary_report(
    stats: DiffSummaryStats,
    colour: bool = True,
    file: TextIO = sys.stdout,
) -> None:
    print(format_summary_report(stats, colour=colour), file=file)
