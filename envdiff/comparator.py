"""Multi-file comparator: compare more than two .env files at once."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set

from envdiff.parser import parse_env_file


@dataclass
class MultiDiffResult:
    """Result of comparing N env files."""

    paths: List[str]
    all_keys: Set[str] = field(default_factory=set)
    # key -> {path: value}  (path absent if key missing in that file)
    matrix: Dict[str, Dict[str, str]] = field(default_factory=dict)

    def keys_present_in_all(self) -> Set[str]:
        """Return keys that appear in every file."""
        return {
            k for k, presence in self.matrix.items()
            if len(presence) == len(self.paths)
        }

    def keys_missing_in_any(self) -> Set[str]:
        """Return keys absent from at least one file."""
        return self.all_keys - self.keys_present_in_all()

    def keys_with_value_mismatch(self) -> Set[str]:
        """Return keys present in all files but with differing values."""
        result: Set[str] = set()
        for key in self.keys_present_in_all():
            values = set(self.matrix[key].values())
            if len(values) > 1:
                result.add(key)
        return result

    def is_consistent(self) -> bool:
        """True when all files share identical keys and values."""
        return not self.keys_missing_in_any() and not self.keys_with_value_mismatch()


def compare_envs(envs: List[Dict[str, str]], paths: List[str]) -> MultiDiffResult:
    """Compare a list of already-parsed env dicts."""
    if len(envs) != len(paths):
        raise ValueError("envs and paths must have the same length")

    all_keys: Set[str] = set()
    for env in envs:
        all_keys |= env.keys()

    matrix: Dict[str, Dict[str, str]] = {k: {} for k in all_keys}
    for path, env in zip(paths, envs):
        for key, value in env.items():
            matrix[key][path] = value

    return MultiDiffResult(paths=list(paths), all_keys=all_keys, matrix=matrix)


def compare_env_files(paths: List[str]) -> MultiDiffResult:
    """Parse and compare multiple .env files."""
    envs = [parse_env_file(p) for p in paths]
    return compare_envs(envs, paths)
