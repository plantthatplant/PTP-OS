# Gaia — Production Deployment (Sprint 13: Go Live)

**Definition of done:** Oskar arrives at Kålaberga, opens the Gaia Control Center in a browser,
works the greenhouse all day, closes the computer in the evening — and never opens Claude Code or
a terminal. This document is what makes that true, and the honest gaps that remain.

## 1. Blockers found → resolved

| Blocker (prevented production) | Resolution (this sprint) |
| --- | --- |
| Everything ran by hand (`python …`, manual imports) | **Supervisor** [`api/run.py`](../api/run.py): one process starts the API and collects on a schedule. |
| Nothing started on boot | **Auto-start at logon** via the Startup folder ([`run/install-startup.ps1`](../run/install-startup.ps1), no admin) or Task Scheduler ([`run/install-autostart.ps1`](../run/install-autostart.ps1)). |
| Snapshot wasn't refreshed automatically | Supervisor runs the **Collector** on startup and every `GAIA_COLLECT_INTERVAL_MIN`; the Morning Brief/Companion recompute per request, so they're always current. |
| No way to know if Gaia was healthy | **`GET /api/v1/health`** (public): overall + per-component status, last snapshot, last analysis, uptime, version. |
| No production logs | **Structured request logging** (JSONL): timestamp, client, endpoint, response time, status, errors → `logs/gaia-requests.jsonl`; events → `logs/gaia.log`. |
| Hardcoded paths/keys | **Env-var config** [`api/config.py`](../api/config.py); engine persistence is repointed from env at startup. |
| No browser interface (Lovable not on this machine) | **Built-in Control Center page** served at `GET /` ([`api/web.py`](../api/web.py)) — pure presentation; bridges until Lovable is connected. |
| Crash would wait for next logon | **Supervised restart loop** in [`run/start-gaia.ps1`](../run/start-gaia.ps1). |

## 2. Configuration — every environment variable

All optional; defaults are safe for a local single-user PC. Nothing is hardcoded.

| Variable | Default | Purpose |
| --- | --- | --- |
| `GAIA_API_KEY` | `gaia-dev-key` | Bearer/X-API-Key for the API. **Set a real value for production.** |
| `GAIA_CORS_ORIGINS` | `*` (reflect any) | comma-separated browser-origin allowlist for production (Lovable + Even Hub origins); other origins get no CORS headers |
| `OPENAI_API_KEY` | — | speech-to-text for `POST /api/v1/ask` (talk to Gaia). Absent → `/ask` answers honestly that voice is unconfigured |
| `ANTHROPIC_API_KEY` | — | Gaia's reasoning for `/api/v1/ask` |
| `GAIA_ANSWER_MODEL` | `claude-opus-4-8` | Claude model `/ask` uses (e.g. `claude-sonnet-4-6` for lower on-glasses latency) |
| `GAIA_HOST` / `GAIA_PORT` | `127.0.0.1` / `8000` | API bind address |
| `GAIA_DATA_DIR` | `<repo>/data` | runtime data (inbox snapshots, logs) |
| `GAIA_APP_DATA_DIR` | `<repo>/app/data` | **persisted Memory / Learning / Observations** |
| `GAIA_LOG_DIR` | `<data>/logs` | request + event logs |
| `GAIA_SNAPSHOT` / `GAIA_PLAN` | `<data>/inbox/latest.json` / `plan-latest.json` | reality / intention streams |
| `GAIA_SOURCE` | `fixture` | Collector source for ticks: `fixture` or `drop-folder` (set this to the real Synopta export) |
| `GAIA_DROP_PATH` | `<data>/inbox/drop` | folder watched when `GAIA_SOURCE=drop-folder` |
| `GAIA_COLLECT_INTERVAL_MIN` | `60` | how often to re-collect |
| `GAIA_VERSION` | `1.0.0` | reported by `/health` |
| `GAIA_PYTHON` / `GAIA_REPO` | discovered | used only by the launcher scripts |

## 3. Start on a brand-new computer (the one documented process)

1. Install Python 3.11+ (this machine: `%LOCALAPPDATA%\Programs\Python\Python312\python.exe`).
2. Copy/clone the repo; no dependencies to install (standard library only).
3. Edit `run/start-gaia.ps1` → set `$Python` and `$Repo` (and a real `GAIA_API_KEY`).
4. Run once: `powershell -ExecutionPolicy Bypass -File run\install-startup.ps1`
   (no admin; for boot-before-logon use `install-autostart.ps1` in an elevated shell).
5. Sign out/in (or run `run\start-gaia.cmd` now). Open **http://127.0.0.1:8000/**.

That's it — every morning is now just "open the browser".

## 4. Reliability — what Gaia survives

| Failure | Behaviour |
| --- | --- |
| **Restart / power outage** | Auto-start relaunches at logon; supervised loop restarts a crash; all writes are atomic. |
| **Missing snapshot** | Service falls back to the last good snapshot, then the bundled sample — never down; `/health` shows degraded. |
| **Invalid snapshot** | Collector quarantines it and keeps the last good one (never publishes a bad file). |
| **Collector failure** | Tick records `source-failed`; last good snapshot stays; API keeps serving; `/health` shows it. |
| **API restart** | Stateless — all state is on disk; it resumes immediately. |

**Persistence:** Memory, Learning, Observations, experiments, answers all live as append-only/
atomic files under `GAIA_APP_DATA_DIR`; published snapshots and their history under
`GAIA_DATA_DIR/inbox`. Nothing important is held only in memory.

## 5. Backup & recovery

- **Back up** two directories (daily is plenty): `GAIA_APP_DATA_DIR` (memory/learning/observations)
  and `GAIA_DATA_DIR/inbox` (snapshots + history). Plain JSON/JSONL — copy them anywhere.
- **Recover:** restore those two directories onto a fresh install and start Gaia. Memory and
  learning are exactly as they were; the Morning Brief recomputes from the latest snapshot.
- **Corruption-safe:** atomic writes mean a file is always either the old or the new version,
  never half-written.

## 6. Health & logging (for Lovable / monitoring)

`GET /api/v1/health` (no key required) returns `status` (ok/degraded/down), `version`,
`uptime_seconds`, `api/brain/memory/learning/collector` statuses, `last_snapshot`
(assembled_at, age, stale), `last_successful_analysis`, and experiment counts — so the Control
Center always knows if Gaia is healthy. Every request is logged as one JSON line with timestamp,
client, endpoint, status, response time, and any error.

## 7. End-to-end production demonstration (verified)

- **Supervisor** started via `python -m api.run`: `/health` → `status: ok`, collector
  `published`, fresh snapshot; `/` served the Control Center; `/api/v1/morning` returned the
  unified brief; unauthenticated request → `401`; requests logged to `gaia-requests.jsonl`.
- **Full founder day over the API only** (`api/control_center_day.py`): Morning → Companion →
  Houses → Voice Note → Observation → Question (confidence Medium→Low) → History → Memory →
  Learning → Evening. The client decided nothing.
- **Auto-start** registered in the Startup folder (`GaiaGoLive.cmd`) — fires at next logon.
- **Persistence**: memory/learning/observations are on disk under `app/data`; an API restart
  re-serves them unchanged.

The one step a chat session cannot perform is a real power-cycle of the greenhouse PC; the
*mechanisms* it relies on are all verified above (atomic on-disk state + auto-start + startup
re-collection), so a reboot resumes Gaia automatically.

## 8. Remaining production risks (honest)

1. **Live greenhouse data is still gated.** `GAIA_SOURCE=fixture` keeps Gaia running on sample
   climate until the **Synopta export/API** is enabled (Sprint 3–4 finding). Switch to
   `drop-folder` + `GAIA_DROP_PATH` (or a future `ApiSource`) the day real exports exist — no
   other change. **This is the top risk to "real" usefulness.**
2. **Auto-start fires at *logon*, not pre-logon boot.** Fine if the PC auto-signs-in (typical for
   a greenhouse terminal); otherwise enable Windows auto-login, or use `install-autostart.ps1`
   (Task Scheduler) in an elevated shell — registering it needs admin (was access-denied here).
3. **Default dev API key.** Set `GAIA_API_KEY` to a real value before relying on it.
4. **Local-only, no TLS.** The API binds `127.0.0.1` for on-PC use; remote/Lovable-cloud access
   needs a hosted URL, TLS, and per-client keys (auth roadmap in `docs/gaia-api.md`). CORS is
   handled — set `GAIA_CORS_ORIGINS` to the browser origins once hosted.
5. **Lovable not yet connected.** The built-in page bridges it; the official Control Center is
   wired when the Lovable project is reachable (contract in `docs/lovable-integration.md`).

## 9. Recommendation for the first real pilot week

1. **Day 0:** set a real `GAIA_API_KEY`, set `$Python`/`$Repo`, run `install-startup.ps1`, reboot,
   confirm the browser opens to a live brief and `/health` is `ok`.
2. **Keep `GAIA_SOURCE=fixture` only until** the Synopta morning export is dropping a file; then
   flip to `drop-folder`. Until then, treat the brief's *climate* as illustrative but use the
   **plan-vs-reality, questions, memory, and learning** for real — they're driven by Oskar's own
   inputs.
3. **Each morning:** open the Control Center, read the one brief, answer at most one question, add
   notes by voice. **Each evening:** glance at `/evening`; close the laptop.
4. **Watch two numbers:** `/health` staleness (is data fresh?) and the learning **hold-rate** (is
   the apprentice getting predictions right?). Back up the two data dirs nightly.
5. **End of week:** review the request log and the learning dashboard; decide whether to invest in
   the Synopta export (unlock live data) and the Lovable connection (richer UI).

## 10. The Final Rule

> Open Gaia Control Center, manage the greenhouse all day, close the computer in the evening,
> never open Claude Code or the terminal.

With auto-start installed and the built-in Control Center at `http://127.0.0.1:8000/`, the daily
loop requires **no terminal and no Claude Code** today. The single thing standing between this
and *fully live* greenhouse data is the Synopta export switch (§8.1) — everything else is in
production.
