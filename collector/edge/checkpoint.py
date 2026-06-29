"""Durable checkpoint — what has already been imported, so nothing is imported twice and a
reboot or power loss never loses or repeats work.

Identity is the file's **content hash** (SHA-256), not its name or timestamp: a scheduled export
that overwrites the same filename each cycle is correctly seen as new when its content differs and
as a duplicate when it is byte-identical. The store also remembers transient-failure retry counts
so a flaky file is retried a bounded number of times, then quarantined rather than retried forever.

Written atomically (temp file + os.replace + fsync), so the checkpoint on disk is always a
complete, valid JSON document even if the machine loses power mid-write.
"""
from __future__ import annotations

import hashlib
import json
import os
from typing import Dict, Optional

from ..log import now_iso

_VERSION = 1
_MAX_PROCESSED = 5000          # bound the history so the file cannot grow without limit


def file_hash(path: str, chunk: int = 1 << 20) -> str:
    """SHA-256 of the file's bytes. Reading in chunks keeps memory flat for large exports."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


class Checkpoint:
    def __init__(self, path: str):
        self.path = path
        self._processed: Dict[str, dict] = {}     # sha256 -> {file, at, status, reading_time}
        self._retries: Dict[str, int] = {}        # filename -> transient retry count
        self._load()

    def _load(self) -> None:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return
        if isinstance(data, dict):
            self._processed = data.get("processed") or {}
            self._retries = data.get("retries") or {}

    def _save(self) -> None:
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        tmp = f"{self.path}.{os.getpid()}.tmp"
        payload = {"version": _VERSION, "updated_at": now_iso(),
                   "processed": self._processed, "retries": self._retries}
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=0)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, self.path)

    # ── dedup ────────────────────────────────────────────────────────────────
    def is_processed(self, digest: str) -> bool:
        return digest in self._processed

    def mark_processed(self, digest: str, filename: str, status: str,
                       reading_time: Optional[str] = None) -> None:
        self._processed[digest] = {"file": filename, "at": now_iso(),
                                   "status": status, "reading_time": reading_time}
        self._retries.pop(filename, None)
        self._prune()
        self._save()

    def _prune(self) -> None:
        if len(self._processed) <= _MAX_PROCESSED:
            return
        # Drop the oldest entries by recorded time, keeping the most recent _MAX_PROCESSED.
        items = sorted(self._processed.items(), key=lambda kv: kv[1].get("at") or "")
        for digest, _ in items[: len(items) - _MAX_PROCESSED]:
            self._processed.pop(digest, None)

    # ── bounded retries for transient failures ────────────────────────────────
    def retry_count(self, filename: str) -> int:
        return self._retries.get(filename, 0)

    def record_retry(self, filename: str) -> int:
        self._retries[filename] = self._retries.get(filename, 0) + 1
        self._save()
        return self._retries[filename]

    def clear_retries(self, filename: str) -> None:
        if filename in self._retries:
            self._retries.pop(filename, None)
            self._save()
