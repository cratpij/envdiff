"""Format and print DiffGraph reports."""
from __future__ import annotations

import sys
from typing import Optional

from envdiff.differ_graph import DiffGraph

_RESET = "\033[0m"
_RED = "\033[31m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"
_BOLD = "\033[1m"


def _colorize(text: str, code: str, color: bool) -> str:
    return f"{code}{text}{_RESET}" if color else text


def format_graph_report(
    graph: DiffGraph,
    filename: Optional[str] = None,
    color: bool = True,
) -> str:
    lines: list[str] = []
    header = f"Diff Graph — {filename}" if filename else "Diff Graph"
    lines.append(_colorize(header, _BOLD, color))
    lines.append(f"Sources: {', '.join(graph.source_names)}")
    lines.append(graph.summary())
    lines.append("")

    inconsistent = set(graph.inconsistent_keys())
    for key in graph.all_keys():
        node = graph.nodes[key]
        if key in inconsistent:
            label = _colorize("MISMATCH", _RED, color)
            lines.append(f"  {key} [{label}]")
            for src, val in node.values.items():
                lines.append(f"    {src}: {val}")
        else:
            missing_in = [
                s for s in graph.source_names if s not in node.values
            ]
            if missing_in:
                label = _colorize("MISSING", _YELLOW, color)
                lines.append(f"  {key} [{label}] — absent in: {', '.join(missing_in)}")
            else:
                label = _colorize("OK", _GREEN, color)
                lines.append(f"  {key} [{label}]")

    return "\n".join(lines)


def print_graph_report(
    graph: DiffGraph,
    filename: Optional[str] = None,
    color: bool = True,
    file=None,
) -> None:
    if file is None:
        file = sys.stdout
    print(format_graph_report(graph, filename=filename, color=color), file=file)
