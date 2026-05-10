"""Archive and restore env snapshots to/from a zip-based archive."""

from __future__ import annotations

import io
import json
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ArchiveEntry:
    path: str
    env: Dict[str, str]
    captured_at: str


@dataclass
class ArchiveResult:
    entries: List[ArchiveEntry] = field(default_factory=list)
    archive_path: Optional[str] = None

    def entry_names(self) -> List[str]:
        return [e.path for e in self.entries]

    def summary(self) -> str:
        count = len(self.entries)
        return f"{count} env file(s) archived to {self.archive_path}"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def archive_envs(
    env_map: Dict[str, Dict[str, str]],
    archive_path: str,
) -> ArchiveResult:
    """Write multiple env dicts into a single zip archive."""
    entries: List[ArchiveEntry] = []
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for source_path, env in env_map.items():
            captured_at = _now_iso()
            entry = ArchiveEntry(path=source_path, env=env, captured_at=captured_at)
            entries.append(entry)
            payload = json.dumps(
                {"path": source_path, "env": env, "captured_at": captured_at},
                indent=2,
            )
            arcname = source_path.lstrip("/").replace("/", "__") + ".json"
            zf.writestr(arcname, payload)
    Path(archive_path).write_bytes(buf.getvalue())
    return ArchiveResult(entries=entries, archive_path=archive_path)


def restore_archive(archive_path: str) -> ArchiveResult:
    """Read all env entries back from a zip archive."""
    entries: List[ArchiveEntry] = []
    with zipfile.ZipFile(archive_path, mode="r") as zf:
        for name in zf.namelist():
            data = json.loads(zf.read(name))
            entries.append(
                ArchiveEntry(
                    path=data["path"],
                    env=data.get("env", {}),
                    captured_at=data.get("captured_at", ""),
                )
            )
    return ArchiveResult(entries=entries, archive_path=archive_path)
