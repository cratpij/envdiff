"""Reporter for CoercionResult — formats coercion output for terminal display."""

from __future__ import annotations

from envdiff.coercer import CoercionResult


def _colorize(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_coercion_report(
    result: CoercionResult,
    filename: str | None = None,
    color: bool = True,
) -> str:
    label = filename or result.source
    lines: list[str] = []

    header = f"=== Coercion Report: {label} ==="
    lines.append(_colorize(header, "1") if color else header)

    changed = result.changed_keys()
    if not changed:
        msg = "  All values remain as strings — nothing coerced."
        lines.append(_colorize(msg, "32") if color else msg)
        return "\n".join(lines)

    for key in sorted(changed):
        original = result.original[key]
        coerced = result.coerced[key]
        type_name = type(coerced).__name__
        row = f"  {key}: {original!r} -> {coerced!r}  ({type_name})"
        if color:
            row = _colorize(f"  {key}", "36") + f": {original!r} -> " + _colorize(repr(coerced), "33") + f"  ({type_name})"
        lines.append(row)

    summary_line = result.summary()
    lines.append("")
    lines.append(_colorize(summary_line, "2") if color else summary_line)
    return "\n".join(lines)


def print_coercion_report(
    result: CoercionResult,
    filename: str | None = None,
    color: bool = True,
) -> None:
    print(format_coercion_report(result, filename=filename, color=color))
