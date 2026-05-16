"""Format and print reports for ResolveResult."""

from __future__ import annotations

from typing import Optional

from envdiff.resolver import ResolveResult


def _colorize(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_resolve_report(
    result: ResolveResult,
    filename: Optional[str] = None,
) -> str:
    label = filename or "(resolved)"
    lines = [
        _colorize(f"=== Resolve Report: {label} ===", "1"),
        f"Layers : {', '.join(result.layer_labels)}",
        result.summary(),
        "",
    ]

    for key in sorted(result.resolved):
        value = result.resolved[key]
        origin = result.origin_of(key) or "?"
        if result.was_overridden(key):
            history = ", ".join(
                f"{lbl}={val}" for lbl, val in result.overridden[key]
            )
            marker = _colorize("OVERRIDDEN", "33")
            lines.append(
                f"  {_colorize(key, '36')} = {value}  [{origin}]  "
                f"({marker}: {history})"
            )
        else:
            lines.append(
                f"  {_colorize(key, '32')} = {value}  [{origin}]"
            )

    return "\n".join(lines)


def print_resolve_report(
    result: ResolveResult,
    filename: Optional[str] = None,
) -> None:
    print(format_resolve_report(result, filename))
