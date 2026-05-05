"""Merge multiple .env files into a unified output, with conflict resolution strategies."""

from typing import Dict, List, Literal, Optional
from envdiff.parser import parse_env_file

MergeStrategy = Literal["first", "last", "error"]


class MergeConflict(Exception):
    """Raised when a key conflict is detected and strategy is 'error'."""

    def __init__(self, key: str, values: Dict[str, str]):
        self.key = key
        self.values = values
        sources = ", ".join(f"{src}={val!r}" for src, val in values.items())
        super().__init__(f"Conflict on key '{key}': {sources}")


def merge_envs(
    env_maps: List[Dict[str, str]],
    sources: Optional[List[str]] = None,
    strategy: MergeStrategy = "last",
) -> Dict[str, str]:
    """Merge a list of env dicts into one.

    Args:
        env_maps: Ordered list of parsed env dicts.
        sources: Optional labels for each env_map (used in conflict messages).
        strategy: How to handle duplicate keys.
            - 'first': keep the value from the first file that defines the key.
            - 'last':  keep the value from the last file that defines the key.
            - 'error': raise MergeConflict if any key appears more than once
                       with differing values.

    Returns:
        A single merged dict.
    """
    if sources is None:
        sources = [str(i) for i in range(len(env_maps))]

    merged: Dict[str, str] = {}
    origins: Dict[str, str] = {}  # key -> source label

    for label, env in zip(sources, env_maps):
        for key, value in env.items():
            if key not in merged:
                merged[key] = value
                origins[key] = label
            else:
                if strategy == "error" and merged[key] != value:
                    raise MergeConflict(
                        key,
                        {origins[key]: merged[key], label: value},
                    )
                elif strategy == "last":
                    merged[key] = value
                    origins[key] = label
                # strategy == "first": do nothing, keep existing value

    return merged


def merge_env_files(
    paths: List[str],
    strategy: MergeStrategy = "last",
) -> Dict[str, str]:
    """Parse and merge multiple .env files.

    Args:
        paths: File paths to parse in order.
        strategy: Conflict resolution strategy passed to merge_envs.

    Returns:
        A single merged dict.
    """
    env_maps = [parse_env_file(p) for p in paths]
    return merge_envs(env_maps, sources=paths, strategy=strategy)
