"""Format and print lint results for human consumption."""

from __future__ import annotations

from typing import Optional

from envdiff.linter import LintResult

_SEVERITY_COLORS = {
    "error": "\033[31m",    # red
    "warning": "\033[33m",  # yellow
    "info": "\033[36m",     # cyan
}
_RESET = "\033[0m"


def _colorize(text: str, severity: str, use_color: bool) -> str:
    if not use_color:
        return text
    color = _SEVERITY_COLORS.get(severity, "")
    return f"{color}{text}{_RESET}"


def format_lint_report(result: LintResult, filename: str = "", use_color: bool = True) -> str:
    """Return a human-readable string report of lint issues."""
    lines = []
    header = f"Lint report{': ' + filename if filename else ''}"
    lines.append(header)
    lines.append("-" * len(header))

    if not result.issues:
        lines.append("  No issues found. ✓")
        return "\n".join(lines)

    for issue in result.issues:
        loc = f"line {issue.line_number}"
        key_part = f" [{issue.key}]" if issue.key else ""
        severity_label = _colorize(issue.severity.upper(), issue.severity, use_color)
        lines.append(f"  {loc}{key_part}  {severity_label}: {issue.message}")

    lines.append("")
    lines.append(result.summary())
    return "\n".join(lines)


def print_lint_report(
    result: LintResult,
    filename: str = "",
    use_color: bool = True,
    output=None,
) -> None:
    """Print the lint report to *output* (defaults to stdout)."""
    import sys
    out = output or sys.stdout
    print(format_lint_report(result, filename=filename, use_color=use_color), file=out)
