#!/usr/bin/env python3
"""Gaia Edge Collector — the daemon that runs all day beside Synopta.

It watches the folder Ridder's scheduled export writes into and keeps `data/inbox/latest.json`
(the file Gaia already consumes) current — automatically, with no terminal, no manual step, and
no Claude. A boot task launches exactly this; the founder never has to think about it.

    python -m collector.edge.run

Configuration is entirely environmental (see `collector/edge/config.py`). It publishes to the
**same** snapshot path the Gaia API reads, derived from the shared `GAIA_*` settings, so the two
processes never disagree about where reality lives.
"""
from __future__ import annotations

import os
import signal
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from collector import _paths
from collector.edge.config import EdgeConfig
from collector.edge.watcher import Watcher


def _align_publish_paths() -> None:
    """Point the collector's output (latest.json, history, quarantine, logs) at the same place the
    Gaia API reads from. Reuses api.config so there is one definition of where data lives."""
    try:
        from api.config import Config
        cfg = Config.from_env()
        _paths.DATA_DIR = cfg.data_dir
        _paths.INBOX_DIR = os.path.join(cfg.data_dir, "inbox")
        _paths.LATEST = cfg.snapshot
        _paths.HISTORY_DIR = os.path.join(_paths.INBOX_DIR, "history")
        _paths.QUARANTINE_DIR = os.path.join(_paths.INBOX_DIR, "quarantine")
        _paths.LOGS_DIR = cfg.log_dir
        for p in (_paths.INBOX_DIR, _paths.HISTORY_DIR, _paths.QUARANTINE_DIR, _paths.LOGS_DIR):
            os.makedirs(p, exist_ok=True)
    except Exception:
        # If the API package isn't importable for some reason, fall back to repo defaults — the
        # Edge Collector still works standalone.
        pass


def _make_event(log_dir: str):
    os.makedirs(log_dir, exist_ok=True)
    path = os.path.join(log_dir, "edge-collector.log")
    # Greenhouse data carries °C, ₂, → etc.; a legacy Windows console codepage must not turn a
    # log line into a crash. UTF-8 with replacement keeps it readable and harmless.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    def event(msg: str):
        line = f"{time.strftime('%Y-%m-%dT%H:%M:%S')}  {msg}"
        try:
            print(line, flush=True)
        except (UnicodeEncodeError, OSError):
            pass
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except OSError:
            pass

    return event


def main() -> int:
    _align_publish_paths()
    cfg = EdgeConfig.from_env()
    event = _make_event(_paths.LOGS_DIR)

    event(f"Gaia Edge Collector starting — import={cfg.import_path}, archive={cfg.archive_path}, "
          f"failed={cfg.failed_path}, interval={cfg.poll_interval_s}s, "
          f"formats={','.join(cfg.supported_formats)}, max_file={cfg.max_file_bytes} bytes")

    watcher = Watcher(cfg, event=event)
    stop = threading.Event()

    def _handle(signum, _frame):
        event(f"signal {signum} received — shutting down…")
        stop.set()

    for sig in (getattr(signal, "SIGINT", None), getattr(signal, "SIGTERM", None)):
        if sig is not None:
            try:
                signal.signal(sig, _handle)
            except (ValueError, OSError):
                pass  # not in main thread / unsupported — KeyboardInterrupt still stops it

    try:
        watcher.run_forever(stop=stop)
    except KeyboardInterrupt:
        stop.set()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
