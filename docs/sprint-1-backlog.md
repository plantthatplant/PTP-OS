# Sprint 1 — Backlog

Task 7 deliverable. Sprint 1's goal: **Morning Intelligence delivering real value
from live greenhouse data through the Provider Layer.** Work is broken into small,
independently deliverable issues, each ready to become a GitHub Issue.

> These are authored here because no GitHub connector is currently available to
> create Issues directly. Once GitHub is connected, each item below can be pushed
> verbatim as an Issue. Labels/estimates use: complexity **S / M / L**.
>
> **Sprint 1 begins only after Sprint 0 is reviewed and approved.**

Suggested labels: `sprint-1`, `provider`, `domain`, `context-engine`,
`decision-engine`, `language-engine`, `memory`, `foundation`.

---

## S1-00 — Decide and document the implementation stack
- **Problem:** No language/framework/runtime is chosen; Sprint 0 deliberately did
  not assume one.
- **Goal:** Pick the stack and record it as an ADR (and a short RFC if the choice
  is contested).
- **Acceptance criteria:**
  - ADR-005 (or RFC) records stack choice with rationale and alternatives.
  - `README` updated with how to build/run once code exists.
- **Dependencies:** Sprint 0 approval.
- **Complexity:** S

## S1-01 — Repo tooling & first commit hygiene
- **Problem:** A real product needs contribution norms and history from commit one.
- **Goal:** Add `.gitignore`, `.editorconfig`, `LICENSE`, `CONTRIBUTING.md`,
  `CODEOWNERS`, `CHANGELOG.md`, and CI skeleton (lint + test run).
- **Acceptance criteria:**
  - CI runs on PRs and passes on an empty/placeholder test.
  - Contribution and ownership docs present.
- **Dependencies:** S1-00.
- **Complexity:** S

## S1-02 — Represent core domain entities in code
- **Problem:** The domain model exists as docs only; the pipeline needs typed
  entities to pass around.
- **Goal:** Implement v1 types for the entities Sprint 1 touches: Greenhouse, Zone,
  Bench, ClimateReading, Observation, PlantBatch, Recommendation, Decision, Memory.
  **No business rules** — types/structures only.
- **Acceptance criteria:**
  - Types match `domain/` docs; canonical units documented.
  - No dependency on any AI model or vendor.
  - Unit tests for construction/validation.
- **Dependencies:** S1-00.
- **Complexity:** M

## S1-03 — Define the GreenhouseProvider interface in code
- **Problem:** The provider boundary is specified but not yet expressed as an
  interface other code can depend on.
- **Goal:** Implement the `GreenhouseProvider` interface + supporting query/result
  types and the provider error taxonomy, per `specs/greenhouse-provider.md`.
- **Acceptance criteria:**
  - Interface compiles and is consumed by a placeholder caller.
  - Error taxonomy and capability types present.
  - No vendor types in the signatures.
- **Dependencies:** S1-02.
- **Complexity:** M

## S1-04 — Provider conformance test suite
- **Problem:** Substitutability (Claude Dispatch → Synopta) must be *proven*, not
  assumed.
- **Goal:** Build the shared conformance test suite from the spec (Section 6).
- **Acceptance criteria:**
  - Suite runs against any `GreenhouseProvider` implementation.
  - Covers domain-type/unit correctness, capability honesty, error mapping, time
    normalization, empty-vs-error.
- **Dependencies:** S1-03.
- **Complexity:** M

## S1-05 — FakeGreenhouseProvider (for development & tests)
- **Problem:** We need to build the pipeline before live data is wired.
- **Goal:** An in-memory provider returning realistic domain data; passes S1-04.
- **Acceptance criteria:**
  - Passes the conformance suite.
  - Configurable sample data for zones/climate/observations.
- **Dependencies:** S1-04.
- **Complexity:** S

## S1-06 — ClaudeDispatchProvider (live greenhouse data)
- **Problem:** Sprint 1 must use *live* greenhouse data.
- **Goal:** Implement `ClaudeDispatchProvider` against the interface; map Claude
  Dispatch data → domain; normalize units/time; contain all vendor specifics.
- **Acceptance criteria:**
  - Passes the conformance suite.
  - Returns live zones and climate readings for at least one real greenhouse.
  - No vendor details leak above the Provider Layer.
- **Dependencies:** S1-03, S1-04. (Needs Claude Dispatch access/credentials.)
- **Complexity:** L

## S1-07 — Context Engine: assemble a minimal daily context
- **Problem:** The Decision Engine needs a coherent "what matters now" picture.
- **Goal:** Assemble a minimal daily context for a greenhouse from latest climate +
  recent observations (+ Memory once available), independent of any AI model.
- **Acceptance criteria:**
  - Given a provider, produces a structured context object.
  - Pure/business-logic only; unit tested with the fake provider.
- **Dependencies:** S1-02, S1-05.
- **Complexity:** M

## S1-08 — Decision Engine: first narrow, explained recommendation
- **Problem:** We need one real, trustworthy recommendation to prove value.
- **Goal:** Implement a single, narrow decision type (e.g. climate-vs-target
  deviation for a zone) producing a structured Recommendation **with rationale and
  cited observations**. No language generation here.
- **Acceptance criteria:**
  - Deterministic, unit-tested logic; no AI dependency.
  - Output includes structured rationale referencing the evidence.
  - Decision type registered in the Decision Library.
- **Dependencies:** S1-07.
- **Complexity:** M

## S1-09 — Language Engine: render the briefing (AI behind an interface)
- **Problem:** Recommendations must be phrased calmly and clearly; the AI model
  must be replaceable.
- **Goal:** Implement the Language Engine behind a `LanguageModel` interface that
  turns a structured Recommendation into calm prose. Include one versioned prompt
  in `prompts/` (one prompt = one feature).
- **Acceptance criteria:**
  - Model accessed only via interface; swappable; a fake/deterministic
    implementation exists for tests.
  - No decisions made or altered here.
  - Prompt versioned in `prompts/` with inputs/outputs documented.
- **Dependencies:** S1-08.
- **Complexity:** M

## S1-10 — Morning Intelligence: minimal daily briefing output
- **Problem:** Deliver the default interface's value end-to-end.
- **Goal:** Compose Context → Decision → Language into a single Morning Intelligence
  briefing for one greenhouse (output structured first, rendered simply).
- **Acceptance criteria:**
  - End-to-end run on live data via `ClaudeDispatchProvider` yields a prioritized,
    explained briefing.
  - Output is structured/screen-independent (G2-ready in principle).
  - Demonstrable as "Friday value".
- **Dependencies:** S1-06, S1-08, S1-09.
- **Complexity:** L

## S1-11 — Memory write path: record decisions & outcomes
- **Problem:** Learning requires capturing what was decided and what happened
  (foundation for RFC-001).
- **Goal:** Persist Decisions and link later Observations as outcomes (write path
  only; read-back into Context is a later sprint).
- **Acceptance criteria:**
  - A Decision can be stored and an outcome later associated, per `domain/memory.md`.
  - Storage is model/vendor-independent; unit tested.
- **Dependencies:** S1-02, S1-08.
- **Complexity:** M

---

## Dependency overview
```
S1-00 → S1-01
S1-00 → S1-02 → S1-03 → S1-04 → S1-05
                         └→ S1-06
S1-02, S1-05 → S1-07 → S1-08 → S1-09 → S1-10
S1-06 ───────────────────────────────→ S1-10
S1-02, S1-08 → S1-11
```

## Sprint 1 "definition of done"
A grower can run Morning Intelligence against live greenhouse data and receive a
prioritized, **explained** briefing; the greenhouse data source sits entirely
behind `GreenhouseProvider` (proven by the conformance suite), so swapping in
Synopta later requires no change above the Provider Layer.
