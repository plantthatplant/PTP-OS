# Sprint 14 — Synopta Edge Integration: Go-Live Checklist

**State at the end of Sprint 14:** the entire receiving chain is built, tested, and runnable.
Gaia imports a real Synopta export into a Canonical Snapshot automatically, with no manual action.
**The only remaining dependency is Ridder enabling the scheduled export** (see
[`docs/ridder-synopta-export-specification.md`](ridder-synopta-export-specification.md)).

This checklist is the exact path from "Ridder turns on the export" to "Gaia is receiving live
greenhouse data".

---

## A. Already done (this sprint — no action needed)

- [x] Edge Collector built: watcher, multi-format parser, pipeline reuse, checkpoint, health, gaps.
- [x] Parser accepts CSV / TSV / Excel / JSON → the existing Canonical Snapshot.
- [x] Reliability proven by tests: dedup, partial-write, reboot/power-loss, retries, freshness guard,
      never-publish-invalid, never-crash. (40 new tests; full suite 106 collector + 9 API green.)
- [x] Collector Health exposed (`python -m collector.edge.health`).
- [x] Environment-only configuration (`collector/edge/config.py`).
- [x] Production launchers: `run/start-edge.cmd`, `run/start-edge.ps1`, `run/install-edge-startup.ps1`.
- [x] Ridder integration package written and ready to send.

## B. Pre-go-live (do now, before Ridder is ready — ~30 min)

1. [ ] **Send the Ridder package** (`docs/ridder-synopta-export-specification.md`) to Ridder/Synopta
       support. Ask them to confirm: export folder path, format, encoding, cadence, and column names.
2. [ ] **Create the drop folders** on this PC (the empty D: drive is the natural home):
       `D:\SynoptaExport\incoming`, `…\archive`, `…\failed`. (The collector also auto-creates them.)
3. [ ] **Decide the import path** and make sure it matches what Ridder will write to. If the server
       writes via a share, share `D:\SynoptaExport\incoming` read-write to the Synopta server account
       only; otherwise have the export write locally on this PC.
4. [ ] **Dry-run with a sample:** drop `collector/tests/fixtures/synopta_export_realistic.csv` into the
       import folder, run `python -m collector.edge.run`, and confirm `data/inbox/latest.json` updates
       and the file moves to `archive\`. Stop it with Ctrl-C.

## C. When Ridder enables the scheduled export (~30–60 min)

5. [ ] **Capture one real export** from the folder. Open it and compare its columns to the alias map
       in `collector/edge/parsers.py` (`DEFAULT_COLUMN_ALIASES`).
6. [ ] **Map any unrecognised columns** — add the real header name(s) to the alias map (one line each),
       or set `SYNOPTA_COLUMN_MAP` env to a JSON override. Re-run the dry-run on the real file and
       confirm the expected observations appear with correct values and units.
7. [ ] **Confirm timestamps** parse as expected (ideally ISO-8601 with offset). If local-time only,
       set `SYNOPTA_DEFAULT_TZ=Europe/Stockholm`.
8. [ ] **Set production env** in `run/start-edge.ps1` (or the environment): `SYNOPTA_IMPORT_PATH`,
       `…_ARCHIVE_PATH`, `…_FAILED_PATH`, `IMPORT_INTERVAL` (≈30 s), `SYNOPTA_FRESHNESS_SLA_S` (≈ 3×
       the export cadence).
9. [ ] **Start the daemon for real:** `run\start-edge.cmd` (or `python -m collector.edge.run`).
10. [ ] **Install auto-start:** `powershell -ExecutionPolicy Bypass -File run\install-edge-startup.ps1`
        so it relaunches at logon alongside Gaia.

## D. Verify live (~15 min, watch 2–3 export cycles)

11. [ ] `python -m collector.edge.health` → `status: ok`, `last_successful_import` recent,
        `current_freshness_seconds` < the cadence, `failed_imports: 0`.
12. [ ] Watch two consecutive exports import: `imports_total` increments, files appear in `archive\`,
        none stuck in `incoming\` or piling up in `failed\`.
13. [ ] Open the Gaia Control Center / API and confirm it now shows **live** values for Houses 1–3
        (not the fixture), with a fresh `assembled_at` and sensible coverage.
14. [ ] Force one failure as a fire-drill: drop a junk `.csv` → confirm it lands in `failed\`,
        `latest.json` is unchanged, a row appears in `data/logs/knowledge-gaps.jsonl`, Health goes
        `degraded`, and the **next good export recovers** to `ok`.

## E. Operational notes

- **If the feed stalls:** Health shows `stale` / rising freshness; `latest.json` keeps the last good
  reading (Gaia reasons from last-known reality, never from nothing). Check the Synopta export job.
- **Logs:** `data/logs/edge-collector.log` (events), `data/logs/collector-YYYYMMDD.jsonl` (per-file),
  `data/logs/knowledge-gaps.jsonl` (declared gaps), `D:\SynoptaExport\failed\` (rejected files).
- **Nothing else changes:** Brain, Observer Network, Learning, Memory, Knowledge Fusion, Gaia API,
  Companion, Lovable, Even G2 are all untouched — they consume the same `latest.json` as before.

---

## Estimated remaining time

| Phase | Owner | Time |
| --- | --- | --- |
| B — pre-go-live setup + send package | us | ~30 min |
| (wait) Ridder enables the export | **Ridder** | their schedule (the real gate) |
| C — map real columns + start daemon | us | ~30–60 min |
| D — verify live over a few cycles | us | ~15 min |

**Total hands-on work remaining: ≈ 1.5–2 hours**, almost all of it confirming the real export's
columns. The genuine wait is **Ridder turning the export on** — once that is done, Gaia receives live
greenhouse data with no further development.
