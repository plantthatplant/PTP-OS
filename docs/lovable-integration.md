# Lovable ↔ Gaia API — Integration (Sprint 12)

**Goal:** Lovable becomes the official Gaia Control Center — a **thin client**. No intelligence
remains inside it; every screen consumes the API; the Brain stays the only source of truth.

## 1. Integration report (honest reality first)

**There is no Lovable codebase in this repository or on this machine** (verified by search — no
`package.json`, no frontend project, no `lovable` directory anywhere reachable). So I cannot edit
Lovable screens that do not exist here. What I *can* do — and did — is make the integration
**real, complete, and verifiable** from this side:

1. **Completed the API surface the sprint requires** — added `GET /api/v1/observations`
   (observation history); the other ten endpoints already existed (Sprint 11).
2. **Built the reference thin client** — [`api/control_center_day.py`](../api/control_center_day.py)
   — a `GaiaClient` that imports **nothing** from the Brain and performs a **complete founder
   day over HTTP only**. This is exactly the pattern Lovable implements; it proves every screen
   can be pure presentation.
3. **Wrote the integration contract** below (screen → endpoint → action) so Lovable can be wired
   screen-by-screen with zero ambiguity.

Once Lovable's repo is accessible, integration is mechanical: each screen calls its endpoint
(§2) and deletes any local logic (§3). **The top blocker is simply access to the Lovable
project** (§5).

## 2. Screen-to-endpoint mapping (what I show · which endpoint · what action)

| Screen | What it shows | Endpoint (GET) | User action (POST) |
| --- | --- | --- | --- |
| **Morning Brief** | the unified one-thought brief, priority, confidence, ask-today, knowledge gaps | `GET /api/v1/morning` | — (read) |
| **Companion** (Even G2 / wrist) | one message + urgency + confidence + ack state | `GET /api/v1/companion` | answer a question → `POST /questions/{id}/answer` |
| **Greenhouses** | per-house status + climate + needs-attention | `GET /api/v1/houses` (`/houses/{id}` for detail) | — |
| **Memory** | lessons learned (zone, lesson, outcome, confidence) | `GET /api/v1/memory` (`/memory/search?q=`) | — |
| **Knowledge Gaps** | the day's worth-asking questions + plan-vs-reality gaps | `GET /api/v1/knowledge-gaps` | answer → `POST /questions/{id}/answer` |
| **Learning** | experiments open/closed, lessons, **calibration (hold-rate)** | `GET /api/v1/learning` | — |
| **Observation History** | posted observations + voice notes, newest first | `GET /api/v1/observations` | — |
| **Voice Notes** | confirmation that the note became an observation | — | `POST /api/v1/voice-notes` `{text, subject}` |
| **Observation Capture** | accepted/rejected count | — | `POST /api/v1/observations` (Canonical only) |
| **Questions** | the day's questions | `GET /api/v1/questions` | `POST /api/v1/questions/{id}/answer` `{answer}` |
| **Evening Review** | lessons today, calibration, open experiments | `GET /api/v1/evening` | — |

Every screen answers the three required questions in that row: *what do I show · which endpoint ·
what action.*

## 3. Removed duplication (the rules Lovable inherits)

Lovable **MUST NOT** (each would be a bug — "if Lovable decides something, that is a bug"):
- compute or alter a brief, priority, recommendation, or confidence;
- score Value-of-Information or decide which question to ask;
- interpret a voice note (the **API** converts text → Canonical Observation);
- merge plan vs reality, or detect deviations;
- write Memory or Learning directly.

Lovable **MAY**: render, cache, filter, search, paginate, format, theme, and lay out — purely
presentation over the API's JSON. By construction there is nothing else to reach: the API
returns *understanding*, and the Brain internals are not exposed.

**Status in this repo:** there is no Lovable code, so there is no duplication to delete *here*.
The reference client proves the target state — a client with **zero** lines of reasoning.

## 4. Remaining mock data

- **In the API:** none for these endpoints — they return real engine/observer output.
- **Upstream of the API (honest):** the morning runs on the **interim snapshot** — the
  screen-read Synopta data or the bundled `sample_snapshot.json` — until the live Synopta export/
  API lands (Sprint 3–4 finding). That is a *data-source* limitation, not a Lovable one, and the
  contract above does not change when it is replaced.
- **In Lovable:** any mock screens it currently ships must be swapped for the endpoints in §2.
  (Cannot be removed from here — the repo is not present.)

## 5. Remaining blockers

1. **Lovable repo access** — the project is not in this repository or on this machine; integration
   of actual screens cannot begin until it is reachable. *(Top blocker.)*
2. **API hosting + per-client auth** — the API runs locally (stdlib server, dev key today). For
   Lovable it needs a hosted URL, TLS, and a per-client API key (auth strategy in
   [`docs/gaia-api.md`](gaia-api.md) §4).
3. **Live greenhouse data** — replace the interim snapshot with the Synopta export/API so the
   morning is fully live (gated externally, as documented).
4. **CORS** — the API will need to allow the Lovable origin once hosted (a server config detail,
   not a contract change).

None of these blocks the *contract*; all are deployment/access steps.

## 6. First complete founder workflow (run, using only the API)

`python api/control_center_day.py` — verified end to end, every screen from an endpoint:

```
Morning Brief   GET /morning   → "House 1 rising disease risk … the classic Botrytis setup."
                                 do-first: increase airflow · ask: is the canopy wet?
Companion       GET /companion  → ▸ House 1: Rising disease risk  [warn, Medium]
Greenhouses     GET /houses     → h1 cuttings exposed to heat (24.2°C/92%) · h2 reading vs plants · h3 settled
Voice Note      POST /voice-notes      → captured "brown spots, bench 3"  [observed-by-human]
Capture         POST /observations     → accepted 1, rejected 0
Question        POST /questions/{id}/answer "No, the canopy is dry" → confidence Medium → Low (worthwhile)
History         GET /observations → the note + the leaf-wetness observation, newest first
Memory          GET /memory       → (lessons accrue as experiments close)
Learning        GET /learning     → 4 open / 0 closed · calibration once closed
Evening         GET /evening      → reviewed; open experiments; calibration
```

**The client decided nothing.** Every value came from the Brain via the API. When Lovable is
wired to these same endpoints, it inherits this exact behaviour — a true thin Control Center,
with the Brain as the single source of truth.
