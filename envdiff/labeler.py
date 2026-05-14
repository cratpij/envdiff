"""Assign human-readable labels to env keys based on configurable rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import Dict, List, Optional, Tuple


@dataclass
class LabelResult:
    """Result of labeling an env dict."""
    env: Dict[str, str]
    labels: Dict[str, List[str]]  # key -> list of matched labels
    rules: List[Tuple[str, str]]  # (pattern, label)
    source: Optional[str] = None

    def keys_with_label(self, label: str) -> List[str]:
        """Return all keys that have the given label."""
        return [k for k, lbls in self.labels.items() if label in lbls]

    def labels_for(self, key: str) -> List[str]:
        """Return labels assigned to *key*, or empty list."""
        return self.labels.get(key, [])

    def unlabeled_keys(self) -> List[str]:
        """Return keys that matched no rule."""
        return [k for k, lbls in self.labels.items() if not lbls]

    def has_label(self, key: str, label: str) -> bool:
        return label in self.labels_for(key)

    def summary(self) -> str:
        labeled = sum(1 for lbls in self.labels.values() if lbls)
        unlabeled = len(self.unlabeled_keys())
        parts = [f"{labeled} labeled"]
        if unlabeled:
            parts.append(f"{unlabeled} unlabeled")
        return ", ".join(parts)


def label_env(
    env: Dict[str, str],
    rules: List[Tuple[str, str]],
    source: Optional[str] = None,
) -> LabelResult:
    """Apply *rules* (pattern, label) to *env* keys.

    A key may match multiple rules and receive multiple labels.
    Rules are evaluated in order; all matching rules apply.
    """
    labels: Dict[str, List[str]] = {}
    for key in env:
        matched: List[str] = []
        for pattern, label in rules:
            if fnmatch(key, pattern):
                matched.append(label)
        labels[key] = matched
    return LabelResult(env=dict(env), labels=labels, rules=list(rules), source=source)


def label_env_file(
    path: str,
    rules: List[Tuple[str, str]],
) -> LabelResult:
    """Parse *path* and label its keys using *rules*."""
    from envdiff.parser import parse_env_file
    env = parse_env_file(path)
    return label_env(env, rules, source=path)
