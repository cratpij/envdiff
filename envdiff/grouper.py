"""Group and summarize env keys by shared prefix or namespace."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.diff import EnvDiffResult


@dataclass
class GroupSummary:
    prefix: str
    keys: List[str] = field(default_factory=list)
    missing_in_right: List[str] = field(default_factory=list)
    missing_in_left: List[str] = field(default_factory=list)
    mismatched: List[str] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return (
            not self.missing_in_right
            and not self.missing_in_left
            and not self.mismatched
        )

    @property
    def issue_count(self) -> int:
        return (
            len(self.missing_in_right)
            + len(self.missing_in_left)
            + len(self.mismatched)
        )


def _extract_prefix(key: str, separator: str = "_") -> str:
    """Return the first segment of a key split by *separator*."""
    parts = key.split(separator, 1)
    return parts[0] if len(parts) > 1 else "__ungrouped__"


def group_diff_by_prefix(
    result: EnvDiffResult,
    separator: str = "_",
    include_ungrouped: bool = True,
) -> Dict[str, GroupSummary]:
    """Return a mapping of prefix -> GroupSummary derived from *result*."""
    groups: Dict[str, GroupSummary] = {}

    all_keys = (
        set(result.missing_in_right)
        | set(result.missing_in_left)
        | set(result.mismatched_values)
    )

    for key in sorted(all_keys):
        prefix = _extract_prefix(key, separator)
        if prefix == "__ungrouped__" and not include_ungrouped:
            continue
        grp = groups.setdefault(prefix, GroupSummary(prefix=prefix))
        grp.keys.append(key)
        if key in result.missing_in_right:
            grp.missing_in_right.append(key)
        if key in result.missing_in_left:
            grp.missing_in_left.append(key)
        if key in result.mismatched_values:
            grp.mismatched.append(key)

    return groups


def top_problem_groups(
    groups: Dict[str, GroupSummary],
    limit: Optional[int] = None,
) -> List[GroupSummary]:
    """Return groups sorted by issue count descending, optionally capped."""
    ranked = sorted(groups.values(), key=lambda g: g.issue_count, reverse=True)
    return ranked[:limit] if limit is not None else ranked
