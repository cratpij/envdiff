"""Format and print ScheduleLog reports."""

from __future__ import annotations

from envdiff.scheduler import ScheduleLog

_RESET = "\033[0m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"


def _colorize(text: str, color: str, use_color: bool) -> str:
    return f"{color}{text}{_RESET}" if use_color else text


def format_schedule_report(
    log: ScheduleLog,
    filename: str = "",
    use_color: bool = True,
) -> str:
    lines: list[str] = []
    header = f"Schedule Report"
    if filename:
        header += f" — {filename}"
    lines.append(_colorize(header, _CYAN, use_color))
    lines.append("-" * 40)

    if not log.entries:
        lines.append("No runs recorded.")
        return "\n".join(lines)

    for entry in log.entries:
        status = "DIFF" if entry.result.has_differences else "OK"
        color = _YELLOW if entry.result.has_differences else _GREEN
        status_str = _colorize(f"[{status}]", color, use_color)
        lines.append(f"{entry.timestamp}  {status_str}  {entry.left_path} vs {entry.right_path}")
        if entry.result.has_differences:
            r = entry.result
            if r.missing_in_right:
                lines.append(f"    Missing in right : {', '.join(sorted(r.missing_in_right))}")
            if r.missing_in_left:
                lines.append(f"    Missing in left  : {', '.join(sorted(r.missing_in_left))}")
            if r.mismatched:
                lines.append(f"    Mismatched       : {', '.join(sorted(r.mismatched))}")

    lines.append("-" * 40)
    lines.append(log.summary())
    return "\n".join(lines)


def print_schedule_report(
    log: ScheduleLog,
    filename: str = "",
    use_color: bool = True,
) -> None:
    print(format_schedule_report(log, filename=filename, use_color=use_color))
