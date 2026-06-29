"""Edge Collector configuration — every value from an environment variable, nothing hardcoded.

Defaults are repo-relative so it runs out of the box on a developer machine; on the greenhouse
PC every path and tuning knob is overridden via the environment (typically set once in
`run/start-edge.cmd` / the Startup task). This mirrors `api/config.py` so the two processes are
configured the same way.

Primary variables (as named in the Sprint-14 brief):

    SYNOPTA_IMPORT_PATH    folder the scheduled Synopta Export writes into   (watched)
    SYNOPTA_ARCHIVE_PATH   where successfully imported files are moved
    SYNOPTA_FAILED_PATH    where unparseable / invalid files are moved
    IMPORT_INTERVAL        poll interval, seconds (how often the folder is scanned)
    MAX_FILE_SIZE          largest export accepted, bytes (a guard against runaway files)
    SUPPORTED_FORMATS      comma list of extensions to import, e.g. "csv,tsv,xlsx,json"

Supporting variables (sensible defaults; override only if needed):

    SYNOPTA_CHECKPOINT_PATH  durable record of what has been imported (reboot/dedup safety)
    SYNOPTA_HEALTH_PATH      durable Collector Health file (read by ops / the API)
    SYNOPTA_STABILITY_SECONDS  a file must be unchanged this long before it is read (debounce)
    SYNOPTA_MAX_RETRIES      transient-failure retries before a file is moved to FAILED
    SYNOPTA_ALLOW_OLDER      "1" to allow an older reading to replace a newer latest.json
    SYNOPTA_FACILITY         facility.json (zone identity / known-absent sensors)
    SYNOPTA_DEFAULT_TZ       assumed timezone for export timestamps that carry none (IANA name)
    SYNOPTA_COLUMN_MAP       optional JSON overriding the column→signal alias map
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

from .. import _paths

_DEFAULT_INBOX = os.path.join(_paths.REPO_ROOT, "data", "inbox")
_DEFAULT_FACILITY = os.path.join(_paths.REPO_ROOT, "collector", "facility.json")


def _env(name: str, default: str) -> str:
    v = os.environ.get(name)
    return v if v not in (None, "") else default


def _env_int(name: str, default: int) -> int:
    try:
        return int(str(_env(name, str(default))).strip())
    except (TypeError, ValueError):
        return default


def _env_bool(name: str, default: bool = False) -> bool:
    v = os.environ.get(name)
    if v in (None, ""):
        return default
    return v.strip().lower() in ("1", "true", "yes", "on")


def _env_formats(name: str, default: Tuple[str, ...]) -> Tuple[str, ...]:
    raw = os.environ.get(name)
    if raw in (None, ""):
        return default
    out = []
    for part in raw.split(","):
        ext = part.strip().lower().lstrip(".")
        if ext:
            out.append("." + ext)
    return tuple(out) or default


@dataclass
class EdgeConfig:
    import_path: str
    archive_path: str
    failed_path: str
    poll_interval_s: int
    max_file_bytes: int
    supported_formats: Tuple[str, ...]      # normalised to (".csv", ".tsv", ...)
    checkpoint_path: str
    health_path: str
    stability_seconds: int
    max_retries: int
    allow_older: bool
    freshness_sla_s: int          # a published reading older than this is reported "stale"
    facility_path: str
    default_tz: str
    column_map: Optional[Dict[str, str]] = field(default=None)

    @classmethod
    def from_env(cls) -> "EdgeConfig":
        import_path = _env("SYNOPTA_IMPORT_PATH", os.path.join(_DEFAULT_INBOX, "drop"))
        column_map = None
        raw_map = os.environ.get("SYNOPTA_COLUMN_MAP")
        if raw_map:
            try:
                parsed = json.loads(raw_map)
                if isinstance(parsed, dict):
                    column_map = {str(k): str(v) for k, v in parsed.items()}
            except json.JSONDecodeError:
                column_map = None  # a bad override is ignored, not fatal — defaults still work
        return cls(
            import_path=import_path,
            archive_path=_env("SYNOPTA_ARCHIVE_PATH", os.path.join(_DEFAULT_INBOX, "archive")),
            failed_path=_env("SYNOPTA_FAILED_PATH", os.path.join(_DEFAULT_INBOX, "failed")),
            poll_interval_s=max(1, _env_int("IMPORT_INTERVAL", 30)),
            max_file_bytes=_env_int("MAX_FILE_SIZE", 16 * 1024 * 1024),
            supported_formats=_env_formats("SUPPORTED_FORMATS", (".csv", ".tsv", ".xlsx", ".json")),
            checkpoint_path=_env("SYNOPTA_CHECKPOINT_PATH",
                                 os.path.join(_DEFAULT_INBOX, "edge-checkpoint.json")),
            health_path=_env("SYNOPTA_HEALTH_PATH",
                             os.path.join(_paths.REPO_ROOT, "data", "logs", "edge-health.json")),
            stability_seconds=max(0, _env_int("SYNOPTA_STABILITY_SECONDS", 5)),
            max_retries=max(0, _env_int("SYNOPTA_MAX_RETRIES", 3)),
            allow_older=_env_bool("SYNOPTA_ALLOW_OLDER", False),
            freshness_sla_s=max(0, _env_int("SYNOPTA_FRESHNESS_SLA_S", 900)),  # 15 min default
            facility_path=_env("SYNOPTA_FACILITY", _DEFAULT_FACILITY),
            default_tz=_env("SYNOPTA_DEFAULT_TZ", "UTC"),
            column_map=column_map,
        )

    def ensure_dirs(self) -> None:
        """Create the folders the watcher owns. The import folder is created too so the
        watcher starts cleanly even before Ridder's first export arrives."""
        for p in (self.import_path, self.archive_path, self.failed_path,
                  os.path.dirname(self.checkpoint_path), os.path.dirname(self.health_path)):
            if p:
                os.makedirs(p, exist_ok=True)
