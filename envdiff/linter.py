"""Lint .env files for common style and correctness issues."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envdiff.parser import parse_env_file


@dataclass
class LintIssue:
    line_number: int
    key: Optional[str]
    message: str
    severity: str  # 'error' | 'warning' | 'info'


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity == "warning" for i in self.issues)

    def summary(self) -> str:
        if not self.issues:
            return "No lint issues found."
        errors = sum(1 for i in self.issues if i.severity == "error")
        warnings = sum(1 for i in self.issues if i.severity == "warning")
        parts = []
        if errors:
            parts.append(f"{errors} error(s)")
        if warnings:
            parts.append(f"{warnings} warning(s)")
        return ", ".join(parts) + " found."


def lint_lines(lines: List[str]) -> LintResult:
    """Lint raw lines from a .env file."""
    issues: List[LintIssue] = []
    seen_keys: dict[str, int] = {}

    for lineno, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            continue

        if "=" not in line:
            issues.append(LintIssue(lineno, None, "Line missing '=' separator.", "error"))
            continue

        key, _, value = line.partition("=")
        key = key.strip()

        if not key:
            issues.append(LintIssue(lineno, None, "Empty key before '='.", "error"))
            continue

        if key != key.upper():
            issues.append(LintIssue(lineno, key, f"Key '{key}' is not uppercase.", "warning"))

        if " " in key:
            issues.append(LintIssue(lineno, key, f"Key '{key}' contains spaces.", "error"))

        if value.strip() == "":
            issues.append(LintIssue(lineno, key, f"Key '{key}' has an empty value.", "info"))

        if key in seen_keys:
            issues.append(LintIssue(
                lineno, key,
                f"Duplicate key '{key}' (first seen on line {seen_keys[key]}).",
                "error",
            ))
        else:
            seen_keys[key] = lineno

    return LintResult(issues=issues)


def lint_env_file(path: str) -> LintResult:
    """Lint a .env file at the given path."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            lines = fh.readlines()
    except FileNotFoundError:
        return LintResult(issues=[LintIssue(0, None, f"File not found: {path}", "error")])
    return lint_lines(lines)
