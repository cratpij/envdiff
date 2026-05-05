"""Formatting and reporting utilities for EnvDiff results."""

from typing import TextIO
import sys

from envdiff.diff import EnvDiffResult


ANSI_RED = "\033[91m"
ANSI_YELLOW = "\033[93m"
ANSI_GREEN = "\033[92m"
ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"


def _colorize(text: str, color: str, use_color: bool) -> str:
    if use_color:
        return f"{color}{text}{ANSI_RESET}"
    return text


def format_report(result: EnvDiffResult, use_color: bool = True) -> str:
    """Return a human-readable diff report as a string."""
    lines = []

    header = f"Comparing: {result.left_name}  vs  {result.right_name}"
    lines.append(_colorize(header, ANSI_BOLD, use_color))
    lines.append("-" * len(header))

    if not result.missing_in_right and not result.missing_in_left and not result.mismatched:
        lines.append(_colorize("No differences found.", ANSI_GREEN, use_color))
        return "\n".join(lines)

    if result.missing_in_right:
        lines.append("")
        label = f"Missing in {result.right_name} ({len(result.missing_in_right)} key(s)):"
        lines.append(_colorize(label, ANSI_RED, use_color))
        for key in sorted(result.missing_in_right):
            lines.append(f"  - {key}")

    if result.missing_in_left:
        lines.append("")
        label = f"Missing in {result.left_name} ({len(result.missing_in_left)} key(s)):"
        lines.append(_colorize(label, ANSI_RED, use_color))
        for key in sorted(result.missing_in_left):
            lines.append(f"  - {key}")

    if result.mismatched:
        lines.append("")
        label = f"Mismatched values ({len(result.mismatched)} key(s)):"
        lines.append(_colorize(label, ANSI_YELLOW, use_color))
        for key in sorted(result.mismatched):
            left_val, right_val = result.mismatched[key]
            lines.append(f"  ~ {key}")
            lines.append(f"      {result.left_name}: {left_val!r}")
            lines.append(f"      {result.right_name}: {right_val!r}")

    lines.append("")
    lines.append(result.summary())
    return "\n".join(lines)


def print_report(
    result: EnvDiffResult,
    use_color: bool = True,
    stream: TextIO = sys.stdout,
) -> None:
    """Print the formatted diff report to *stream*."""
    print(format_report(result, use_color=use_color), file=stream)
