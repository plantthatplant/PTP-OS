"""Production configuration — everything from environment variables, no hardcoded paths or keys.

Defaults are repo-relative so it runs out of the box, but every value is overridable via env so
the same code runs on any machine. See docs/production-deployment.md for the full variable list.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from . import _paths


def _env(name, default):
    v = os.environ.get(name)
    return v if v not in (None, "") else default


def load_env_file(path: str | None = None) -> None:
    """Load KEY=VALUE lines from a git-ignored `.env` at the repo root into os.environ, WITHOUT
    overriding anything already set in the real environment (so an explicit `FOO=… python -m
    api.run` still wins). This is where secrets belong — OPENAI_API_KEY, ANTHROPIC_API_KEY,
    GAIA_API_KEY — a local file git ignores, never committed, never in code, never returned by
    the API. Missing file is fine (the defaults still run)."""
    path = path or os.path.join(_paths.REPO_ROOT, ".env")
    try:
        with open(path, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key and val and key not in os.environ:   # blank values don't claim the var
                    os.environ[key] = val
    except FileNotFoundError:
        pass


@dataclass
class Config:
    host: str
    port: int
    api_key: str
    data_dir: str          # runtime data (inbox, logs)
    app_data_dir: str      # Brain store (memory / learning / observations)
    log_dir: str
    snapshot: str          # the snapshot the service reads (reality)
    plan: str              # plan/intention stream
    source: str            # collector source for scheduled ticks: fixture | drop-folder
    drop_path: str         # folder for drop-folder source
    collect_interval_min: int
    version: str

    @property
    def is_dev_key(self) -> bool:
        return self.api_key == "gaia-dev-key"

    @classmethod
    def from_env(cls) -> "Config":
        data_dir = _env("GAIA_DATA_DIR", os.path.join(_paths.REPO_ROOT, "data"))
        return cls(
            host=_env("GAIA_HOST", "127.0.0.1"),
            # GAIA_PORT wins; else honour a host-injected $PORT (Render/Railway/Heroku); else 8000.
            port=int(_env("GAIA_PORT", _env("PORT", "8000"))),
            api_key=_env("GAIA_API_KEY", "gaia-dev-key"),
            data_dir=data_dir,
            app_data_dir=_env("GAIA_APP_DATA_DIR", os.path.join(_paths.APP_DIR, "data")),
            log_dir=_env("GAIA_LOG_DIR", os.path.join(data_dir, "logs")),
            snapshot=_env("GAIA_SNAPSHOT", os.path.join(data_dir, "inbox", "latest.json")),
            plan=_env("GAIA_PLAN", os.path.join(data_dir, "inbox", "plan-latest.json")),
            source=_env("GAIA_SOURCE", "fixture"),
            drop_path=_env("GAIA_DROP_PATH", os.path.join(data_dir, "inbox", "drop")),
            collect_interval_min=int(_env("GAIA_COLLECT_INTERVAL_MIN", "60")),
            version=_env("GAIA_VERSION", "1.0.0"),
        )
