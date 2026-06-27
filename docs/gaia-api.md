# Gaia API v1 — the nervous system of PTP-OS

**Status:** built (stdlib, dependency-free) · [`api/`](../api/). **Audit that preceded it:**
[`docs/gaia-api-audit.md`](gaia-api-audit.md). **Constraint honored:** the Brain, Memory,
Learning, and Observer Network are **integrated, not redesigned** — the API is a thin gateway
over the existing engines.

## 1. Architecture

```
   Lovable   Even G2   Mobile   Desktop   DJI   Humanoid        ← clients (presentation only)
      └─────────┴─────────┴───────┬────────┴──────┘
                                  │  HTTP, JSON, /api/v1, API key
                          ┌───────▼────────┐
                          │   Gaia API     │  api/server.py  (transport: routes, auth, errors)
                          │   GaiaService  │  api/service.py (the one gateway / facade)
                          └───────┬────────┘
        the ONLY importer of ↓ (clients never reach past this line)
   Morning Analysis · Knowledge Gap · Fusion · Lifecycle/Memory(store) · Providers · Observers
                          = the Brain (single source of truth, unchanged)
```

The API is the **only** public interface. No client imports `store`, `knowledge_gap`,
`lifecycle`, `fusion`, a provider, or an observer — those are reached *only* through
`GaiaService`, which composes them once and returns **understanding** (narrative, priority,
confidence, questions, gaps, learning) — never storage paths, vendor names, or observer identity.

**Design properties (all met):** stateless (state lives in the snapshot + store, not the API),
simple (stdlib), versioned (`/api/v1`), observable (uniform JSON + version header + error
envelope), documented (this file), testable (8 service tests, isolated store), backwards-
compatible (additive-only, §6), and provider-/observer-/client-independent (§ the three
questions).

## 2. Endpoints (the minimum public interface)

| Method | Path | Returns / accepts |
| --- | --- | --- |
| GET | `/api/v1/morning` | Unified brief, priority, confidence, first recommendation, knowledge gaps |
| GET | `/api/v1/houses` · `/houses/{id}` | Per-house understanding (climate, status, needs-attention) |
| GET | `/api/v1/memory` · `/memory/search?q=` | Lessons learned (sanitised) |
| GET | `/api/v1/knowledge-gaps` | The day's worth-asking questions + plan-vs-reality gaps |
| GET | `/api/v1/learning` | Experiments open/closed, lessons, **calibration (hold-rate)** |
| POST | `/api/v1/observations` | **Canonical Observations only** (no client-specific payloads) |
| GET | `/api/v1/questions` | The day's questions |
| POST | `/api/v1/questions/{id}/answer` | `{ "answer": "..." }` → confidence before/after, worthwhile |
| POST | `/api/v1/voice-notes` | `{ "text": "...", "subject": "h1" }` → the API makes a Canonical Observation |
| GET | `/api/v1/companion` | One message + urgency + confidence + acknowledgement state (Even G2) |
| GET | `/api/v1/evening` | Daily review: lessons today, calibration, open experiments |

Run it: `python api/server.py` · End-to-end demo (many clients, one API): `python api/demo.py`.

## 3. Request / response examples

```
GET /api/v1/morning           Authorization: Bearer <key>
200 →
{ "greenhouse": "Kålaberga",
  "brief": "House 1 rising disease risk (humid, stagnant, wet canopy). Meanwhile the plan
            expected 60 × Pentas around 2026-07-17. … the classic Botrytis setup.",
  "priority": "House 1 — increase air movement now …",
  "first_recommendation": "increase air movement now …",
  "confidence": "Medium",
  "ask_today": "Do you see condensation or a wet canopy in House 1?",
  "knowledge_gaps": [ { "id": "kq-2026-06-27-prevent-0", "text": "…canopy wet?", "value": 0.6 } ] }

GET /api/v1/companion          → { "message": "House 1: Rising disease risk", "urgency": "warn",
                                   "confidence": "Medium", "acknowledged": false, "question_id": null }

POST /api/v1/voice-notes       { "text": "brown spots, bench 3", "subject": "h1" }
201 → { "accepted": true, "observation": { "subject": "h1", "kind": "note",
        "value": "brown spots, bench 3", "method": "observed-by-human", "confidence": "medium" } }

POST /api/v1/observations      { "subject": "h2", "kind": "leaf-wetness", "value": "wet",
                                 "source": "dji", "method": "vision-inferred", "confidence": "medium" }
201 → { "accepted": 1, "rejected": 0 }

POST /api/v1/questions/kq-.../answer   { "answer": "No, the canopy is dry" }
200 → { "confidence_before": "Medium", "confidence_after": "Low", "worthwhile": true }
```

## 4. Authentication strategy

- **v1 (now):** a per-client **API key** sent as `Authorization: Bearer <key>` (or `X-API-Key`).
  The server checks it against `GAIA_API_KEY`; a dev key is used if unset. Missing/invalid →
  `401`.
- **Roadmap (not built):** one key *per client* (Lovable, Even, DJI…) so they can be revoked
  independently; **scopes** (read-only vs observation-write vs answer); rotate via env/secret
  store; TLS in front; OAuth/mTLS for third parties. Keys are credentials — never in code, never
  in a client bundle; the API never returns them.

## 5. Versioning strategy

- Version in the path: `/api/v1`. A response header `Gaia-API-Version: v1` echoes it.
- **Additive-only within a version:** new fields and new endpoints may appear; existing fields
  never change meaning or disappear (backwards compatible).
- A breaking change means `/api/v2`, served alongside v1 during a deprecation window
  (`Deprecation`/`Sunset` headers). Clients pin a version.

## 6. Error handling

Uniform envelope, correct status:
```
{ "error": { "code": "unauthorized", "message": "missing or invalid API key" } }
```
`400` bad request (malformed JSON / bad body) · `401` unauthorized · `404` not found ·
`405` method not allowed · `500` internal (message truncated; **never a stack trace to a
client**). Every error is JSON; clients never parse HTML or tracebacks.

## 7. Event model

- **v1 is pull (request/response).** A client GETs `/companion` or `/morning` when it needs the
  current understanding; this is stateless and simple, and fits Even G2's glance model.
- **Future push (designed, not built):** a lightweight stream — Server-Sent Events at
  `/api/v1/companion/stream` or per-client webhooks — emitting events like `companion.message`,
  `observation.accepted`, `question.answered`, `confidence.changed`. The payloads are the *same*
  understanding objects as the pull endpoints, so adding push changes transport, not contract.
  (Deferred until a client needs real-time, e.g. a drone mid-flight.)

## 8. Migration & refactoring plan

From the audit ([`gaia-api-audit.md`](gaia-api-audit.md)): the morning orchestration is currently
duplicated across `gaia.py`, `companion/daily.py`, and the demos. Plan (Brain untouched):
1. **Ship `GaiaService` + the HTTP API** *(done this sprint — additive)*.
2. **Re-point existing clients at the service**, deleting their duplicated orchestration:
   `companion/daily.py` → `service.morning()/companion()/evening()`; `gaia.py` cmd_* → the
   service; demos → thin clients of the API.
3. **Convention + test:** only `api/` may import `store`, `knowledge_gap`, `lifecycle`, `fusion`,
   providers, observers.
4. **Lovable** is built as a pure presentation client of `/api/v1` from day one.

## 9. Clients — one API, no Brain change

| Client | Reads | Writes | Notes |
| --- | --- | --- | --- |
| **Lovable** (web) | `/morning`, `/houses`, `/memory`, `/knowledge-gaps`, `/learning`, `/evening` | `/voice-notes` | presentation only: render/cache/filter/search; **no reasoning** |
| **Even G2** | `/companion` | `/questions/{id}/answer`, `/voice-notes` | exactly the glance surface, nothing more |
| **Mobile / Desktop** | all GETs | `/voice-notes`, `/observations` | the information + capture surfaces |
| **DJI / cameras** | — | `/observations` (Canonical, `vision-inferred`) | an observer client; posts observations |
| **Humanoid (future)** | `/companion`, `/houses` | `/observations`, `/questions/{id}/answer` | observer + surface; same endpoints |

Every client uses the **same** endpoints and the same Canonical Observation contract. None can
reason; there is nothing to reach but understanding.

## 10. The three questions

- **If Lovable disappeared tomorrow, would Gaia continue working?** **Yes.** Lovable is a
  presentation client; nothing in the API or Brain depends on it. The CLI, the Companion runner,
  and any other client keep working against the same endpoints. *(Proven: the API runs and is
  exercised by `api/demo.py` with no Lovable present — there is no Lovable code at all.)*
- **If Even G2 disappeared tomorrow, would Gaia continue working?** **Yes.** Even G2 consumes
  `/companion` and posts answers/voice-notes — all general endpoints other clients also use.
  Remove it and the understanding is still served; the phone or desktop reads the same data.
- **If a completely new client appeared tomorrow, could it be connected in under a day?** **Yes.**
  It needs only an API key and HTTP: GET the understanding it wants, POST Canonical Observations
  or answers. No Brain change, no new endpoint, no new contract — the DJI and humanoid rows above
  are connected purely by *using* the existing API. (The `api/demo.py` already stands up five
  different "clients" against one server in one file.)

All three are "yes" **by construction**: clients are interchangeable behind one gateway that
returns only understanding — the same substitutability ADR-002 gave data sources and RFC-004 gave
observers, now extended to clients. The Brain remains the single source of truth.
