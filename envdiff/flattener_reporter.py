"""Reporting utilities for FlattenResult."""

from __future__ import annotations

from typing import Optional

from envdiff.flattener import FlattenResult


def _colorize(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_flatten_report(
    result: FlattenResult,
    filename: Optional[str] = None,
    use_color: bool = True,
) -> str:
    lines: list[str] = []

    header = "Flatten Report"
    if filename:
        header += f" — {filename}"
    lines.append(_colorize(header, "1") if use_color else header)
    lines.append("")

    summary = result.summary()
    lines.append((_colorize(summary, "32") if not result.has_collisions() else _colorize(summary, "33")) if use_color else summary)

    if result.flat:
        lines.append("")
        lines.append("Keys:")
        for key in sorted(result.flat):
            source = result.sources.get(key, "?")
            value = result.flat[key]
            collision_marker = " [COLLISION]" if key in result.collisions else ""
            marker_colored = _colorize(collision_marker, "31") if use_color and collision_marker else collision_marker
            lines.append(f"  {key}={value!r}  (from: {source}){marker_colored}")

    if result.collisions:
        lines.append("")
        lines.append(_colorize("Collisions:", "31") if use_color else "Collisions:")
        for key, srcs in sorted(result.collisions.items()):
            lines.append(f"  {key}: competed by {', '.join(srcs)}")

    return "\n".join(lines)


def print_flatten_report(
    result: FlattenResult,
    filename: Optional[str] = None,
    use_color: bool = True,
) -> None:
    print(format_flatten_report(result, filename=filename, use_color=use_color))
