"""Schedule periodic env diff checks and report changes over time."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, List, Optional

from envdiff.diff import EnvDiffResult, diff_envs
from envdiff.parser import parse_env_file


@dataclass
class ScheduleEntry:
    timestamp: str
    left_path: str
    right_path: str
    result: EnvDiffResult


@dataclass
class ScheduleLog:
    entries: List[ScheduleEntry] = field(default_factory=list)

    def add(self, entry: ScheduleEntry) -> None:
        self.entries.append(entry)

    @property
    def total_runs(self) -> int:
        return len(self.entries)

    @property
    def runs_with_differences(self) -> int:
        return sum(1 for e in self.entries if e.result.has_differences)

    def summary(self) -> str:
        if not self.entries:
            return "No scheduled runs recorded."
        return (
            f"Runs: {self.total_runs} | "
            f"With differences: {self.runs_with_differences} | "
            f"Clean: {self.total_runs - self.runs_with_differences}"
        )


def _now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def run_once(
    left_path: str,
    right_path: str,
    log: Optional[ScheduleLog] = None,
    on_diff: Optional[Callable[[ScheduleEntry], None]] = None,
) -> ScheduleEntry:
    left = parse_env_file(left_path)
    right = parse_env_file(right_path)
    result = diff_envs(left, right)
    entry = ScheduleEntry(
        timestamp=_now_iso(),
        left_path=left_path,
        right_path=right_path,
        result=result,
    )
    if log is not None:
        log.add(entry)
    if on_diff is not None and result.has_differences:
        on_diff(entry)
    return entry


def run_schedule(
    left_path: str,
    right_path: str,
    interval_seconds: float,
    max_runs: int,
    log: Optional[ScheduleLog] = None,
    on_diff: Optional[Callable[[ScheduleEntry], None]] = None,
) -> ScheduleLog:
    if log is None:
        log = ScheduleLog()
    for i in range(max_runs):
        run_once(left_path, right_path, log=log, on_diff=on_diff)
        if i < max_runs - 1:
            time.sleep(interval_seconds)
    return log
