"""Snapshot .env files and compare against saved snapshots."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Optional

from envdiff.parser import parse_env_file
from envdiff.diff import diff_envs, EnvDiffResult


@dataclass
class Snapshot:
    """A saved snapshot of a .env file."""

    path: str
    captured_at: str
    values: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "captured_at": self.captured_at,
            "values": self.values,
        }

    @staticmethod
    def from_dict(data: dict) -> "Snapshot":
        return Snapshot(
            path=data["path"],
            captured_at=data["captured_at"],
            values=data.get("values", {}),
        )


def capture_snapshot(env_path: str) -> Snapshot:
    """Parse an env file and return a Snapshot."""
    values = parse_env_file(env_path)
    captured_at = datetime.now(timezone.utc).isoformat()
    return Snapshot(path=env_path, captured_at=captured_at, values=values)


def save_snapshot(snapshot: Snapshot, snapshot_path: str) -> None:
    """Persist a snapshot to a JSON file."""
    with open(snapshot_path, "w", encoding="utf-8") as fh:
        json.dump(snapshot.to_dict(), fh, indent=2)


def load_snapshot(snapshot_path: str) -> Snapshot:
    """Load a previously saved snapshot from a JSON file."""
    if not os.path.exists(snapshot_path):
        raise FileNotFoundError(f"Snapshot file not found: {snapshot_path}")
    with open(snapshot_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return Snapshot.from_dict(data)


def diff_against_snapshot(
    env_path: str, snapshot_path: str
) -> tuple[EnvDiffResult, Snapshot]:
    """Diff the current state of an env file against a saved snapshot.

    Returns the diff result and the loaded snapshot.
    """
    snapshot = load_snapshot(snapshot_path)
    current = parse_env_file(env_path)
    result = diff_envs(snapshot.values, current, left_label="snapshot", right_label="current")
    return result, snapshot
