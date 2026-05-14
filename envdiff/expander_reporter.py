"""Format and print expansion reports."""

from __future__ import annotations

from envdiff.expander import ExpansionResult


def _colorize(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_expansion_report(
    result: ExpansionResult,
    filename: str | None = None,
    use_color: bool = True,
) -> str:
    label = filename or result.source
    lines: list[str] = []

    header = f"Expansion Report: {label}"
    lines.append(_colorize(header, "1") if use_color else header)
    lines.append("")

    if result.is_clean():
        msg = "  ✔ All references resolved successfully."
        lines.append(_colorize(msg, "32") if use_color else msg)
    else:
        for key, refs in sorted(result.unresolved.items()):
            ref_list = ", ".join(refs)
            msg = f"  ✘ {key}: unresolved → {ref_list}"
            lines.append(_colorize(msg, "31") if use_color else msg)

    lines.append("")

    resolved_count = len(result.expanded) - len(result.unresolved)
    footer = (
        f"  Resolved: {resolved_count}  "
        f"Unresolved: {len(result.unresolved)}  "
        f"Total: {len(result.expanded)}"
    )
    lines.append(footer)

    return "\n".join(lines)


def print_expansion_report(
    result: ExpansionResult,
    filename: str | None = None,
    use_color: bool = True,
) -> None:
    print(format_expansion_report(result, filename=filename, use_color=use_color))
