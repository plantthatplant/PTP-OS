"""DropFolderSource — read the newest export file Synopta drops into a folder.

This is the safe, vendor-supported live path (the file-drop bridge recommended in
docs/dispatch-runtime-investigation.md): Synopta — or a scheduled job — writes an export
file to a known folder; the Collector picks up the most recent one. Read-only; it never
writes into, deletes from, or otherwise touches the source folder, and never connects to
the live control bus or the GUI.

The exact export *format* is an open question (specs/gaia-collector.md §11); v1 expects the
established vendor JSON shape. When a real export's shape is confirmed, only this source's
parsing changes — translation and everything above stay put.
"""
from __future__ import annotations

import json
import os

from .base import SynoptaSource, SourceError


# A real greenhouse export is a handful of KB. Refuse anything wildly larger so a corrupt or
# hostile file in the drop folder cannot exhaust memory in json.load.
_MAX_EXPORT_BYTES = 16 * 1024 * 1024  # 16 MB — generous, but bounded


class DropFolderSource(SynoptaSource):
    label = "drop-folder"

    def __init__(self, path: str, pattern_exts=(".json",), max_bytes: int = _MAX_EXPORT_BYTES):
        if not path:
            raise SourceError("drop-folder source needs a folder path (--path)")
        self.path = path
        self.exts = tuple(e.lower() for e in pattern_exts)
        self.max_bytes = max_bytes

    def _newest_file(self) -> str:
        if not os.path.isdir(self.path):
            raise SourceError(f"drop folder does not exist: {self.path}")
        candidates = [
            os.path.join(self.path, n) for n in os.listdir(self.path)
            if n.lower().endswith(self.exts) and os.path.isfile(os.path.join(self.path, n))
        ]
        if not candidates:
            raise SourceError(f"no export files ({', '.join(self.exts)}) in {self.path}")
        # Newest by modification time — the most recent reading the greenhouse dropped.
        return max(candidates, key=os.path.getmtime)

    def fetch(self) -> dict:
        newest = self._newest_file()
        size = os.path.getsize(newest)
        if size > self.max_bytes:
            raise SourceError(
                f"export file is implausibly large ({size} bytes > {self.max_bytes}): {newest}")
        try:
            with open(newest, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except json.JSONDecodeError as e:
            raise SourceError(f"export file is not valid JSON ({newest}): {e}") from e
        except UnicodeDecodeError as e:
            raise SourceError(f"export file is not valid UTF-8 ({newest}): {e}") from e
        # Record which file we read, so provenance/logs can trace it. (Ignored downstream
        # if absent; never invents data.)
        if isinstance(raw, dict):
            raw.setdefault("_source_file", os.path.basename(newest))
        return raw
