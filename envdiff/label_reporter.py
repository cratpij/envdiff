"""Format and print LabelResult reports."""
from __future__ import annotations

import sys
from typing import Optional

from envdiff.labeler import LabelResult


def _colorize(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_label_report(
    result: LabelResult,
    filename: Optional[str] = None,
    color: bool = True,
) -> str:
    """Return a human-readable string describing the label assignments."""
    lines: list[str] = []
    header = f"Label report"
    if filename or result.source:
        header += f" — {filename or result.source}"
    lines.append(_colorize(header, "1") if color else header)
    lines.append("")

    if not result.env:
        lines.append("  (no keys)")
        return "\n".join(lines)

    for key in sorted(result.env):
        lbls = result.labels_for(key)
        if lbls:
            tag_str = ", ".join(lbls)
            label_part = _colorize(f"[{tag_str}]", "36") if color else f"[{tag_str}]"
        else:
            label_part = _colorize("[unlabeled]", "33") if color else "[unlabeled]"
        lines.append(f"  {key} {label_part}")

    lines.append("")
    summary = result.summary()
    lines.append(_colorize(summary, "32") if color else summary)
    return "\n".join(lines)


def print_label_report(
    result: LabelResult,
    filename: Optional[str] = None,
    color: bool = True,
) -> None:
    print(format_label_report(result, filename=filename, color=color), file=sys.stdout)
