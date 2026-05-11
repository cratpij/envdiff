"""Freeze an env dict into an immutable snapshot and detect drift from it."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.parser import parse_env_file


@dataclass
class FreezeResult:
    path: str
    frozen: Dict[str, str]
    checksum: str
    drifted_keys: List[str] = field(default_factory=list)
    added_keys: List[str] = field(default_factory=list)
    removed_keys: List[str] = field(default_factory=list)

    @property
    def has_drift(self) -> bool:
        return bool(self.drifted_keys or self.added_keys or self.removed_keys)

    def summary(self) -> str:
        if not self.has_drift:
            return f"{self.path}: no drift detected"
        parts = []
        if self.drifted_keys:
            parts.append(f"{len(self.drifted_keys)} changed")
        if self.added_keys:
            parts.append(f"{len(self.added_keys)} added")
        if self.removed_keys:
            parts.append(f"{len(self.removed_keys)} removed")
        return f"{self.path}: drift detected — " + ", ".join(parts)


def _checksum(env: Dict[str, str]) -> str:
    serialised = json.dumps(env, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialised.encode()).hexdigest()


def freeze_env(env: Dict[str, str], path: str = "<dict>") -> FreezeResult:
    """Capture a frozen baseline from an env dict."""
    checksum = _checksum(env)
    return FreezeResult(path=path, frozen=dict(env), checksum=checksum)


def freeze_env_file(path: str) -> FreezeResult:
    """Parse *path* and freeze it."""
    env = parse_env_file(path)
    return freeze_env(env, path=path)


def detect_drift(
    baseline: FreezeResult,
    current: Dict[str, str],
    path: Optional[str] = None,
) -> FreezeResult:
    """Compare *current* env against *baseline* and return a drift report."""
    resolved_path = path or baseline.path
    checksum = _checksum(current)

    frozen_keys = set(baseline.frozen)
    current_keys = set(current)

    drifted = [k for k in frozen_keys & current_keys if baseline.frozen[k] != current[k]]
    added = sorted(current_keys - frozen_keys)
    removed = sorted(frozen_keys - current_keys)

    return FreezeResult(
        path=resolved_path,
        frozen=baseline.frozen,
        checksum=checksum,
        drifted_keys=sorted(drifted),
        added_keys=added,
        removed_keys=removed,
    )


def detect_drift_from_file(baseline: FreezeResult, path: str) -> FreezeResult:
    """Load *path* and detect drift against *baseline*."""
    current = parse_env_file(path)
    return detect_drift(baseline, current, path=path)
