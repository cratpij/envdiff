"""envdiff.pinner — Pin current env values as a locked reference snapshot.

Allows users to 'pin' the current state of an env file so that future
diffs can be compared against this pinned baseline, not just another file.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Optional

from envdiff.parser import parse_env_file
from envdiff.diff import diff_envs, EnvDiffResult


@dataclass
class PinnedEnv:
    source: str
    pinned_at: str
    values: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "pinned_at": self.pinned_at,
            "values": self.values,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PinnedEnv":
        return cls(
            source=data.get("source", ""),
            pinned_at=data.get("pinned_at", ""),
            values=data.get("values", {}),
        )


def pin_env(env: Dict[str, str], source: str = "<dict>") -> PinnedEnv:
    """Create a PinnedEnv from an in-memory mapping."""
    ts = datetime.now(timezone.utc).isoformat()
    return PinnedEnv(source=source, pinned_at=ts, values=dict(env))


def pin_env_file(path: str) -> PinnedEnv:
    """Parse *path* and return a PinnedEnv capturing its current values."""
    env = parse_env_file(path)
    return pin_env(env, source=os.path.abspath(path))


def save_pin(pin: PinnedEnv, dest: str) -> None:
    """Serialise *pin* to *dest* as JSON."""
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(pin.to_dict(), fh, indent=2)


def load_pin(path: str) -> PinnedEnv:
    """Load a previously saved PinnedEnv from *path*."""
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return PinnedEnv.from_dict(data)


def diff_against_pin(pin: PinnedEnv, current: Dict[str, str]) -> EnvDiffResult:
    """Compare *current* env mapping against a pinned baseline."""
    return diff_envs(pin.values, current)


def diff_file_against_pin(pin: PinnedEnv, path: str) -> EnvDiffResult:
    """Parse *path* and diff it against *pin*."""
    current = parse_env_file(path)
    return diff_against_pin(pin, current)
