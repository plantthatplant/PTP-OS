#!/usr/bin/env python3
"""Gaia production supervisor — the one process that runs all day.

It starts the API, collects the newest greenhouse snapshot on a schedule, and stays available.
No manual scripts, no terminal, no Claude Code: a boot task launches this, and the founder opens
the Control Center in a browser. It is resilient — a failed collection, a missing/invalid
snapshot, or a transient error never takes the API down; memory/learning/observations persist on
disk and survive restart.

    python -m api.run           # foreground (the boot task runs exactly this)
"""
from __future__ import annotations

import json
import os
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.config import Config
from api import health, server
from api.service import GaiaService


def _configure_paths(cfg: Config):
    """Point the engines' persistence at the configured dirs (env-driven, no hardcoded paths)."""
    from collector import _paths as cp
    cp.DATA_DIR = cfg.data_dir
    cp.INBOX_DIR = os.path.join(cfg.data_dir, "inbox")
    cp.LATEST = cfg.snapshot
    cp.HISTORY_DIR = os.path.join(cp.INBOX_DIR, "history")
    cp.QUARANTINE_DIR = os.path.join(cp.INBOX_DIR, "quarantine")
    cp.LOGS_DIR = cfg.log_dir

    from greenhouse_brain import store
    d = cfg.app_data_dir
    store._DATA_DIR = d
    store._FEEDBACK_FILE = os.path.join(d, "feedback.jsonl")
    store._EXPERIMENTS_FILE = os.path.join(d, "experiments-open.json")
    store._MEMORIES_FILE = os.path.join(d, "memories.jsonl")
    store._QUESTIONS_FILE = os.path.join(d, "questions-today.json")
    store._ANSWERS_FILE = os.path.join(d, "answers.jsonl")
    store._QEVAL_FILE = os.path.join(d, "question-evaluations.jsonl")
    store._INTERACTIONS_FILE = os.path.join(d, "interactions.jsonl")
    store._TODAY_SNAPSHOT_FILE = os.path.join(d, "today-snapshot.json")
    store._YESTERDAY_FILE = os.path.join(d, "yesterday-signals.json")
    for p in (d, cfg.data_dir, cp.INBOX_DIR, cfg.log_dir):
        os.makedirs(p, exist_ok=True)


def _make_loggers(cfg: Config):
    os.makedirs(cfg.log_dir, exist_ok=True)
    req_path = os.path.join(cfg.log_dir, "gaia-requests.jsonl")
    evt_path = os.path.join(cfg.log_dir, "gaia.log")

    def request_logger(rec):
        try:
            with open(req_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        except OSError:
            pass

    def event(msg):
        line = f"{time.strftime('%Y-%m-%dT%H:%M:%S')}  {msg}"
        print(line, flush=True)
        try:
            with open(evt_path, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except OSError:
            pass

    return request_logger, event


def _collect_once(cfg: Config, event) -> str:
    """Run the Collector once. Never raises — a failure leaves the last good snapshot in place."""
    try:
        from collector.collect import run as collect_run
        code = collect_run(source_name=cfg.source,
                           path=cfg.drop_path if cfg.source != "fixture" else None)
        status = {0: "published", 2: "quarantined", 3: "source-failed"}.get(code, f"exit-{code}")
    except Exception as e:                                  # collection must never crash the day
        status = f"error: {str(e)[:120]}"
    snap_at = None
    try:
        with open(cfg.snapshot, "r", encoding="utf-8") as f:
            snap_at = json.load(f).get("assembled_at")
    except (OSError, json.JSONDecodeError):
        pass
    health.STATE.record_collection(status, snap_at)
    event(f"collection: {status}  (snapshot {snap_at})")
    return status


def _collection_loop(cfg: Config, event, stop: threading.Event):
    _collect_once(cfg, event)                              # collect immediately on startup
    interval = max(60, cfg.collect_interval_min * 60)
    while not stop.wait(interval):                         # then on the configured cadence
        _collect_once(cfg, event)


def main() -> int:
    cfg = Config.from_env()
    health.STATE.version = cfg.version
    _configure_paths(cfg)
    request_logger, event = _make_loggers(cfg)

    event(f"Gaia {cfg.version} starting — source={cfg.source}, interval={cfg.collect_interval_min}m, "
          f"data={cfg.data_dir}" + ("  [WARNING: using dev API key]" if cfg.is_dev_key else ""))

    service = GaiaService(snapshot_path=cfg.snapshot, plan_path=cfg.plan)
    httpd = server.serve(host=cfg.host, port=cfg.port, service=service,
                         api_key=cfg.api_key, logger=request_logger)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    event(f"API live at http://{cfg.host}:{httpd.server_address[1]}/  "
          f"(Control Center)  ·  /api/v1/health")

    stop = threading.Event()
    loop = threading.Thread(target=_collection_loop, args=(cfg, event, stop), daemon=True)
    loop.start()
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        event("shutting down…")
        stop.set()
        httpd.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
