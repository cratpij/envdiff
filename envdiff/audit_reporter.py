"""Format and print audit reports."""

import sys
from typing import List

from envdiff.auditor import AuditResult


def _colorize(text: str, color: str) -> str:
    codes = {"green": "\033[32m", "red": "\033[31m", "yellow": "\033[33m", "reset": "\033[0m"}
    return f"{codes.get(color, '')}{text}{codes['reset']}"


def format_audit_report(result: AuditResult, color: bool = True) -> str:
    lines = []
    status = "PASS" if result.passed else "FAIL"
    status_color = "green" if result.passed else "red"
    label = _colorize(f"[{status}]", status_color) if color else f"[{status}]"
    lines.append(f"{label} Audit: {result.path}")
    lines.append(f"  Score  : {result.score.score:.0f}/100 (Grade: {result.score.grade()})")
    lines.append(f"  Keys   : {result.profile.total_keys} total, {result.profile.empty_count} empty")

    error_count = sum(1 for i in result.lint.issues if i.level == "error")
    warn_count = sum(1 for i in result.lint.issues if i.level == "warning")
    lint_str = f"{error_count} error(s), {warn_count} warning(s)"
    lint_color = "red" if error_count else ("yellow" if warn_count else "green")
    lines.append(f"  Lint   : {_colorize(lint_str, lint_color) if color else lint_str}")

    val_str = "valid" if result.validation.is_valid() else result.validation.summary()
    val_color = "green" if result.validation.is_valid() else "red"
    lines.append(f"  Valid  : {_colorize(val_str, val_color) if color else val_str}")

    for note in result.notes:
        lines.append(f"  Note   : {note}")
    return "\n".join(lines)


def format_multi_audit_report(results: List[AuditResult], color: bool = True) -> str:
    sections = [format_audit_report(r, color=color) for r in results]
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    summary_color = "green" if passed == total else "red"
    summary = f"{passed}/{total} files passed audit"
    sections.append(_colorize(summary, summary_color) if color else summary)
    return "\n\n".join(sections)


def print_audit_report(result: AuditResult, color: bool = True) -> None:
    print(format_audit_report(result, color=color), file=sys.stdout)
