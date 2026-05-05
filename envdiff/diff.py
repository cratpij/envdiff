"""Diff module for comparing parsed .env dictionaries."""

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class EnvDiffResult:
    """Holds the result of comparing two .env files."""

    base_name: str
    compare_name: str
    missing_in_compare: List[str] = field(default_factory=list)
    missing_in_base: List[str] = field(default_factory=list)
    mismatched: Dict[str, tuple] = field(default_factory=dict)

    @property
    def has_differences(self) -> bool:
        """Return True if any differences were found."""
        return bool(
            self.missing_in_compare or self.missing_in_base or self.mismatched
        )

    def summary(self) -> str:
        """Return a human-readable summary of the diff."""
        lines = [
            f"Comparing '{self.base_name}' vs '{self.compare_name}'",
            "-" * 50,
        ]

        if self.missing_in_compare:
            lines.append(f"\nKeys in '{self.base_name}' but missing in '{self.compare_name}':")
            for key in sorted(self.missing_in_compare):
                lines.append(f"  - {key}")

        if self.missing_in_base:
            lines.append(f"\nKeys in '{self.compare_name}' but missing in '{self.base_name}':")
            for key in sorted(self.missing_in_base):
                lines.append(f"  + {key}")

        if self.mismatched:
            lines.append("\nMismatched values:")
            for key in sorted(self.mismatched):
                base_val, cmp_val = self.mismatched[key]
                lines.append(f"  ~ {key}")
                lines.append(f"      {self.base_name}: {base_val!r}")
                lines.append(f"      {self.compare_name}: {cmp_val!r}")

        if not self.has_differences:
            lines.append("\nNo differences found.")

        return "\n".join(lines)


def diff_envs(
    base: Dict[str, str],
    compare: Dict[str, str],
    base_name: str = "base",
    compare_name: str = "compare",
) -> EnvDiffResult:
    """Compare two env dictionaries and return a diff result.

    Args:
        base: The reference environment dictionary.
        compare: The environment dictionary to compare against base.
        base_name: Label for the base environment.
        compare_name: Label for the compare environment.

    Returns:
        An EnvDiffResult describing all differences.
    """
    base_keys: Set[str] = set(base.keys())
    compare_keys: Set[str] = set(compare.keys())

    result = EnvDiffResult(base_name=base_name, compare_name=compare_name)
    result.missing_in_compare = list(base_keys - compare_keys)
    result.missing_in_base = list(compare_keys - base_keys)

    for key in base_keys & compare_keys:
        if base[key] != compare[key]:
            result.mismatched[key] = (base[key], compare[key])

    return result
