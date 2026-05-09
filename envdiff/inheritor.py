"""Inheritance resolution for .env files.

Allows a child env to inherit from a parent env, with the child's
values taking precedence over the parent's.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.parser import parse_env_file


@dataclass
class InheritanceResult:
    """Result of merging a parent env into a child env."""

    resolved: Dict[str, str]
    inherited_keys: List[str]  # keys taken from parent (absent in child)
    overridden_keys: List[str]  # keys present in both; child wins
    child_only_keys: List[str]  # keys only in child
    parent_path: Optional[str] = None
    child_path: Optional[str] = None

    def summary(self) -> str:
        lines = []
        if self.parent_path or self.child_path:
            lines.append(
                f"parent={self.parent_path or '<dict>'}  "
                f"child={self.child_path or '<dict>'}"
            )
        lines.append(f"inherited : {len(self.inherited_keys)}")
        lines.append(f"overridden: {len(self.overridden_keys)}")
        lines.append(f"child-only: {len(self.child_only_keys)}")
        return "\n".join(lines)


def inherit_envs(
    parent: Dict[str, str],
    child: Dict[str, str],
    *,
    parent_path: Optional[str] = None,
    child_path: Optional[str] = None,
) -> InheritanceResult:
    """Merge *parent* into *child*, child values take precedence."""
    resolved: Dict[str, str] = {**parent, **child}

    inherited = [k for k in parent if k not in child]
    overridden = [k for k in child if k in parent]
    child_only = [k for k in child if k not in parent]

    return InheritanceResult(
        resolved=resolved,
        inherited_keys=sorted(inherited),
        overridden_keys=sorted(overridden),
        child_only_keys=sorted(child_only),
        parent_path=parent_path,
        child_path=child_path,
    )


def inherit_env_files(parent_path: str, child_path: str) -> InheritanceResult:
    """Load two .env files and compute the inheritance result."""
    parent = parse_env_file(parent_path)
    child = parse_env_file(child_path)
    return inherit_envs(parent, child, parent_path=parent_path, child_path=child_path)
