"""Aggregated summary statistics across multiple EnvDiffResult objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.diff import EnvDiffResult


@dataclass
class DiffSummaryStats:
    total_files: int = 0
    total_keys_compared: int = 0
    total_missing_in_right: int = 0
    total_missing_in_left: int = 0
    total_mismatched: int = 0
    files_with_differences: int = 0
    per_file: Dict[str, Dict[str, int]] = field(default_factory=dict)

    @property
    def total_issues(self) -> int:
        return self.total_missing_in_right + self.total_missing_in_left + self.total_mismatched

    @property
    def is_clean(self) -> bool:
        return self.total_issues == 0

    def summary(self) -> str:
        if self.is_clean:
            return f"All {self.total_files} file pair(s) are identical."
        return (
            f"{self.files_with_differences}/{self.total_files} file pair(s) have differences "
            f"({self.total_missing_in_right} missing-right, "
            f"{self.total_missing_in_left} missing-left, "
            f"{self.total_mismatched} mismatched)."
        )


def compute_summary(results: List[tuple[str, EnvDiffResult]]) -> DiffSummaryStats:
    """Compute aggregated statistics from a list of (label, EnvDiffResult) pairs."""
    stats = DiffSummaryStats(total_files=len(results))

    for label, result in results:
        mr = len(result.missing_in_right)
        ml = len(result.missing_in_left)
        mm = len(result.mismatched)
        all_keys = set(result.missing_in_right) | set(result.missing_in_left) | set(result.mismatched)

        stats.total_keys_compared += len(all_keys)
        stats.total_missing_in_right += mr
        stats.total_missing_in_left += ml
        stats.total_mismatched += mm

        if mr or ml or mm:
            stats.files_with_differences += 1

        stats.per_file[label] = {
            "missing_in_right": mr,
            "missing_in_left": ml,
            "mismatched": mm,
        }

    return stats
