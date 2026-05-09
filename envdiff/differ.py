"""Multi-file sequential differ: compare a list of env files pairwise."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple

from envdiff.diff import EnvDiffResult, diff_envs
from envdiff.parser import parse_env_file


@dataclass
class PairwiseDiff:
    """Diff result between two adjacent env files."""

    left_path: str
    right_path: str
    result: EnvDiffResult

    @property
    def has_differences(self) -> bool:
        return bool(
            self.result.missing_in_right
            or self.result.missing_in_left
            or self.result.mismatched
        )

    def summary(self) -> str:
        parts = []
        if self.result.missing_in_right:
            parts.append(f"{len(self.result.missing_in_right)} missing in right")
        if self.result.missing_in_left:
            parts.append(f"{len(self.result.missing_in_left)} missing in left")
        if self.result.mismatched:
            parts.append(f"{len(self.result.mismatched)} mismatched")
        if not parts:
            return "no differences"
        return ", ".join(parts)


@dataclass
class SequentialDiffResult:
    """Collection of pairwise diffs across a sequence of env files."""

    pairs: List[PairwiseDiff] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return all(not p.has_differences for p in self.pairs)

    @property
    def total_pairs(self) -> int:
        return len(self.pairs)

    def pairs_with_differences(self) -> List[PairwiseDiff]:
        return [p for p in self.pairs if p.has_differences]

    def summary(self) -> str:
        dirty = len(self.pairs_with_differences())
        if dirty == 0:
            return f"All {self.total_pairs} pair(s) are identical."
        return f"{dirty}/{self.total_pairs} pair(s) have differences."


def diff_sequence(
    envs: List[Tuple[str, dict]],
) -> SequentialDiffResult:
    """Diff a list of (name, env_dict) tuples pairwise (left→right, right→next, …)."""
    pairs: List[PairwiseDiff] = []
    for i in range(len(envs) - 1):
        left_name, left_env = envs[i]
        right_name, right_env = envs[i + 1]
        result = diff_envs(left_env, right_env)
        pairs.append(PairwiseDiff(left_path=left_name, right_path=right_name, result=result))
    return SequentialDiffResult(pairs=pairs)


def diff_sequence_files(paths: List[str]) -> SequentialDiffResult:
    """Parse a list of .env file paths and diff them sequentially."""
    if len(paths) < 2:
        raise ValueError("At least two file paths are required for a sequential diff.")
    envs = [(p, parse_env_file(p)) for p in paths]
    return diff_sequence(envs)
