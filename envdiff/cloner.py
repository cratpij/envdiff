"""Clone an env dict or file, optionally filtering or renaming keys."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.parser import parse_env_file


@dataclass
class CloneResult:
    source_path: str
    dest_path: str
    cloned: Dict[str, str]
    skipped: List[str] = field(default_factory=list)
    renamed: Dict[str, str] = field(default_factory=dict)  # old_key -> new_key

    def total_cloned(self) -> int:
        return len(self.cloned)

    def summary(self) -> str:
        parts = [f"Cloned {self.total_cloned()} key(s) from '{self.source_path}' to '{self.dest_path}'."]
        if self.skipped:
            parts.append(f"Skipped {len(self.skipped)} key(s): {', '.join(self.skipped)}.")
        if self.renamed:
            renames = ", ".join(f"{old}->{new}" for old, new in self.renamed.items())
            parts.append(f"Renamed {len(self.renamed)} key(s): {renames}.")
        return " ".join(parts)


def clone_env(
    source: Dict[str, str],
    source_path: str,
    dest_path: str,
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    renames: Optional[Dict[str, str]] = None,
) -> CloneResult:
    """Clone *source* env dict, applying optional include/exclude/rename rules."""
    renames = renames or {}
    exclude_set = set(exclude or [])
    include_set = set(include) if include is not None else None

    cloned: Dict[str, str] = {}
    skipped: List[str] = []
    applied_renames: Dict[str, str] = {}

    for key, value in source.items():
        if include_set is not None and key not in include_set:
            skipped.append(key)
            continue
        if key in exclude_set:
            skipped.append(key)
            continue
        dest_key = renames.get(key, key)
        if dest_key != key:
            applied_renames[key] = dest_key
        cloned[dest_key] = value

    return CloneResult(
        source_path=source_path,
        dest_path=dest_path,
        cloned=cloned,
        skipped=skipped,
        renamed=applied_renames,
    )


def clone_env_file(
    source_path: str,
    dest_path: str,
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    renames: Optional[Dict[str, str]] = None,
) -> CloneResult:
    """Parse *source_path* and clone its contents, writing result to *dest_path*."""
    source = parse_env_file(source_path)
    result = clone_env(
        source=source,
        source_path=source_path,
        dest_path=dest_path,
        include=include,
        exclude=exclude,
        renames=renames,
    )
    lines = [f"{k}={v}\n" for k, v in result.cloned.items()]
    with open(dest_path, "w", encoding="utf-8") as fh:
        fh.writelines(lines)
    return result
