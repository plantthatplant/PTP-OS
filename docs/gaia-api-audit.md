# Gaia API — Architectural Audit & Duplication Report (Sprint 11, before implementation)

**Done before any API code, per the sprint.** I searched the whole repository for client/UI
reasoning, business-logic duplication, and direct Brain access. Findings below decide the
refactor.

## 1. Headline finding

**There is no "Lovable" / frontend / UI code in this repository.** Searches for
`lovable|frontend|react|.tsx` match only the *word* "presentation" in docs and engine comments.
So there is no Lovable biological-reasoning to remove **today** — but there is also **no gateway
between clients and the Brain**, and the *existing* clients (the Python entry scripts) already
exhibit the exact coupling the API exists to prevent. Lovable, when it is built, must inherit the
rules in §4 from day one.

## 2. The real duplication: morning orchestration, repeated per client

The pipeline *snapshot → SnapshotProvider → MorningAnalysisEngine → open experiments →
knowledge_gap.generate → (fusion)* is **re-wired independently** in at least four places:

| Client / entry point | Re-orchestrates the Brain? | Direct Brain/Memory access |
| --- | --- | --- |
| `app/gaia.py` (`cmd_morning`, `cmd_walk`, `cmd_evening`) | **Yes** — full pipeline (51 engine refs) | `store` (Memory), `knowledge_gap`, `lifecycle`, `decision` via analysis |
| `companion/daily.py` | **Yes** — pipeline + fusion + plan | `store`, `knowledge_gap`, `fusion`, `plan_vs_reality` |
| `companion/demo_mornings.py` | **Yes** — pipeline + fusion | `knowledge_gap`, `fusion` |
| `companion/demo_walk.py` | **Yes** — pipeline | `knowledge_gap`, `store`, `lifecycle` |
| `app/import_snapshot.py`, `collector/demo_pipeline.py` | Partial pipeline | importer, provider, analysis |

**This is duplicated orchestration, not duplicated reasoning** — the reasoning still lives once,
in the engines (good; RFC-003 held). But every client re-implements *how to compose the engines
for a morning*, and every client reaches **directly** into Memory (`store`), Knowledge
(`knowledge_gap`), and Learning (`lifecycle`). That is precisely what the API mandate forbids
clients from doing. If a fifth client (Lovable) is added, it would copy the composition a fifth
time — and likely drift.

## 3. What is *not* a problem (so we don't "fix" it)

- **The engines hold the reasoning once.** No client re-computes Plant State, confidence, or VoI;
  they call the engines. The Brain is already the single source of *reasoning*.
- **`views.py` is presentation** (it renders briefs to text) — a renderer, not logic. It is fine,
  though it lives inside the Brain package; clients may keep rendering, but should render *Gaia's
  understanding*, not derive it.
- **Provider/Observer independence already holds** (ADR-002, RFC-004) — clients never see Synopta
  or observer identity; they see Canonical Observations / domain types.

## 4. The gap the API closes

There is **one missing layer: a single gateway** that composes the engines once and is the only
thing clients touch. Today's clients ARE the gateway, four times over. The fix is **not** to
change the Brain — it is to introduce a thin **GaiaService** facade (the API's core) that:

- performs the morning/evening/companion composition **once**,
- exposes only **Gaia's understanding** (narrative, priority, confidence, questions, gaps,
  learning) — never storage paths, vendor names, or observer identity,
- and becomes the **only** importer of `store`, `knowledge_gap`, `lifecycle`, `fusion`, the
  providers, and the observers.

Clients (CLI, Companion, Lovable, Even G2, DJI, future robots) then call **endpoints**, not
engines.

## 5. Refactoring plan (incremental, Brain untouched)

1. **Add `GaiaService`** (the facade) + the HTTP API over it. *(This sprint — additive; nothing
   in the Brain changes.)*
2. **Re-point the existing clients at the service**, one at a time, deleting their duplicated
   orchestration:
   - `companion/daily.py` → call `service.morning()` / `service.companion()` / `service.evening()`.
   - `app/gaia.py` `cmd_morning/walk/evening` → call the service.
   - demos → thin clients of the service (or of the HTTP API).
3. **Forbid new direct Brain imports from clients** by convention (and a lint/test): only
   `api/` may import `store`, `knowledge_gap`, `lifecycle`, `fusion`, providers, observers.
4. **Lovable** is built as a pure presentation client of the HTTP API from the start (§ rules in
   `docs/gaia-api.md`).

No engine, Memory, Learning, or Observer-Network redesign — this is consolidation behind one
door, exactly the "integrate, don't redesign" constraint.

## 6. Rules carried into the API (for every client, including Lovable)

A client MAY: render, cache, filter, search, present. A client MUST NOT: perform biological
reasoning, generate recommendations, modify confidence, write Memory directly, or duplicate Brain
logic. The API returns understanding; clients show it. These rules are enforced by the API being
the *only* surface — there is nothing else for a client to reach.
