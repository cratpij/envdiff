"""Format and print EnvScore reports."""
from __future__ import annotations

import sys
from typing import List

from envdiff.scorer import EnvScore

_GRADE_COLORS = {
    "A": "\033[92m",  # green
    "B": "\033[94m",  # blue
    "C": "\033[93m",  # yellow
    "D": "\033[33m",  # dark yellow
    "F": "\033[91m",  # red
}
_RESET = "\033[0m"


def _colorize(text: str, color: str, use_color: bool) -> str:
    if not use_color:
        return text
    return f"{color}{text}{_RESET}"


def format_score_report(score: EnvScore, use_color: bool = True) -> str:
    """Return a multi-line string summarising the score."""
    lines: List[str] = []
    color = _GRADE_COLORS.get(score.grade, "")
    grade_str = _colorize(f"[{score.grade}]  {score.score}/100", color, use_color)
    lines.append(f"Score for {score.path}: {grade_str}")

    if score.notes:
        lines.append("  Deductions:")
        for note in score.notes:
            lines.append(f"    - {note}")
    else:
        ok = _colorize("No issues found.", "\033[92m", use_color)
        lines.append(f"  {ok}")

    return "\n".join(lines)


def format_multi_score_report(
    scores: List[EnvScore], use_color: bool = True
) -> str:
    """Format multiple scores with a summary line."""
    parts = [format_score_report(s, use_color=use_color) for s in scores]
    avg = sum(s.score for s in scores) // len(scores) if scores else 0
    parts.append(f"\nAverage score: {avg}/100")
    return "\n\n".join(parts)


def print_score_report(
    score: EnvScore, use_color: bool = True, file=None
) -> None:
    """Print a score report to *file* (default: stdout)."""
    if file is None:
        file = sys.stdout
    print(format_score_report(score, use_color=use_color), file=file)
