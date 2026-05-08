"""Detect and remove duplicate keys within a single .env file."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class DeduplicationResult:
    """Result of scanning an env mapping for duplicate keys."""

    source: str
    duplicates: Dict[str, List[str]]  # key -> list of all values seen
    deduped: Dict[str, str]           # key -> winning (last) value

    def has_duplicates(self) -> bool:
        return bool(self.duplicates)

    def summary(self) -> str:
        if not self.has_duplicates():
            return f"{self.source}: no duplicate keys found"
        keys = ", ".join(sorted(self.duplicates))
        return (
            f"{self.source}: {len(self.duplicates)} duplicate key(s) found: {keys}"
        )


def find_duplicates(lines: List[str]) -> Tuple[Dict[str, List[str]], Dict[str, str]]:
    """Parse *lines* tracking every value assigned to each key.

    Returns:
        duplicates  – keys that appeared more than once, mapping to all values
        deduped     – final env dict (last assignment wins, same as most shells)
    """
    seen: Dict[str, List[str]] = {}
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"\'')
        seen.setdefault(key, []).append(value)

    duplicates = {k: v for k, v in seen.items() if len(v) > 1}
    deduped = {k: v[-1] for k, v in seen.items()}
    return duplicates, deduped


def deduplicate_env(lines: List[str], source: str = "<input>") -> DeduplicationResult:
    """Analyse *lines* from an env file and return a :class:`DeduplicationResult`."""
    duplicates, deduped = find_duplicates(lines)
    return DeduplicationResult(source=source, duplicates=duplicates, deduped=deduped)


def deduplicate_env_file(path: str | Path) -> DeduplicationResult:
    """Read *path* and return a :class:`DeduplicationResult`."""
    p = Path(path)
    lines = p.read_text(encoding="utf-8").splitlines()
    return deduplicate_env(lines, source=str(p))
