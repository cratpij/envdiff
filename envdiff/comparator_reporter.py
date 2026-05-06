"""Reporting utilities for MultiDiffResult."""

from __future__ import annotations

import sys
from typing import Optional

from envdiff.comparator import MultiDiffResult

_RESET = "\033[0m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_GREEN = "\033[32m"
_BOLD = "\033[1m"


def _c(text: str, code: str, use_color: bool) -> str:
    return f"{code}{text}{_RESET}" if use_color else text


def format_multi_diff_report(
    result: MultiDiffResult,
    use_color: bool = True,
) -> str:
    lines: list[str] = []

    header = f"Comparing {len(result.paths)} file(s):"
    lines.append(_c(header, _BOLD, use_color))
    for p in result.paths:
        lines.append(f"  {p}")
    lines.append("")

    if result.is_consistent():
        lines.append(_c("✔ All files are consistent.", _GREEN, use_color))
        return "\n".join(lines)

    missing = sorted(result.keys_missing_in_any())
    if missing:
        lines.append(_c("Keys missing in one or more files:", _RED, use_color))
        for key in missing:
            present_in = sorted(result.matrix[key].keys())
            absent_in = sorted(set(result.paths) - set(present_in))
            lines.append(f"  {key}")
            lines.append(f"    present in : {', '.join(present_in)}")
            lines.append(f"    absent in  : {', '.join(absent_in)}")
        lines.append("")

    mismatched = sorted(result.keys_with_value_mismatch())
    if mismatched:
        lines.append(_c("Keys with mismatched values:", _YELLOW, use_color))
        for key in mismatched:
            lines.append(f"  {key}")
            for path, value in sorted(result.matrix[key].items()):
                lines.append(f"    {path}: {value!r}")
        lines.append("")

    return "\n".join(lines)


def print_multi_diff_report(
    result: MultiDiffResult,
    use_color: bool = True,
    file: Optional[object] = None,
) -> None:
    if file is None:
        file = sys.stdout
    print(format_multi_diff_report(result, use_color=use_color), file=file)  # type: ignore[arg-type]
