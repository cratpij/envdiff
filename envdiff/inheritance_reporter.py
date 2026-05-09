"""Human-readable reporter for InheritanceResult."""

from __future__ import annotations

import sys
from typing import Optional

from envdiff.inheritor import InheritanceResult


def _colorize(text: str, code: str) -> str:
    """Wrap *text* in an ANSI colour *code* when stdout is a TTY."""
    if sys.stdout.isatty():
        return f"\033[{code}m{text}\033[0m"
    return text


def format_inheritance_report(
    result: InheritanceResult,
    filename: Optional[str] = None,
) -> str:
    """Return a formatted string report for *result*."""
    header_label = filename or result.child_path or "env"
    lines = [
        _colorize(f"=== Inheritance Report: {header_label} ===", "1"),
        f"  Parent : {result.parent_path or '<dict>'}",
        f"  Child  : {result.child_path or '<dict>'}",
        "",
    ]

    if result.inherited_keys:
        lines.append(_colorize(f"  Inherited from parent ({len(result.inherited_keys)}):", "36"))
        for k in result.inherited_keys:
            lines.append(f"    + {k} = {result.resolved[k]}")

    if result.overridden_keys:
        lines.append(_colorize(f"  Overridden by child ({len(result.overridden_keys)}):", "33"))
        for k in result.overridden_keys:
            lines.append(f"    ~ {k} = {result.resolved[k]}")

    if result.child_only_keys:
        lines.append(_colorize(f"  Child-only keys ({len(result.child_only_keys)}):", "32"))
        for k in result.child_only_keys:
            lines.append(f"    * {k} = {result.resolved[k]}")

    if not any([result.inherited_keys, result.overridden_keys, result.child_only_keys]):
        lines.append(_colorize("  Both files are empty.", "90"))

    return "\n".join(lines)


def print_inheritance_report(
    result: InheritanceResult,
    filename: Optional[str] = None,
) -> None:
    """Print the inheritance report to stdout."""
    print(format_inheritance_report(result, filename=filename))
