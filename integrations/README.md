# integrations/

External systems PTP OS talks to: greenhouse **data providers** and other
third-party services. Everything here sits at the edge of the system, behind a
stable internal interface, so the core never depends on a specific external
vendor.

## Greenhouse data providers

The Provider Layer is the most important integration point in PTP OS. It answers
one question for the rest of the system: *"What is happening in the greenhouse?"*
— without the rest of the system caring how that answer was obtained.

| Provider | Role | Status |
| --- | --- | --- |
| `ClaudeDispatchProvider` | Initial greenhouse data provider | Built (Sprint 1) |
| `SnapshotProvider` | Serves any Canonical Snapshot to the engines | Built |
| `SynoptaProvider` | Long-term provider via Synopta Pro/API | Future |

The contract both must satisfy is defined in
[`specs/greenhouse-provider.md`](../specs/greenhouse-provider.md). The decision to
abstract providers is recorded in
[`adr/ADR-002-provider-abstraction.md`](../adr/ADR-002-provider-abstraction.md).

## Gaia Collector — the first real Synopta bridge

[`collector/`](../collector/) is the local component that reads Synopta data and writes it as a
Canonical Snapshot to `data/inbox/latest.json`, which Gaia consumes via `SnapshotProvider`
unchanged. It contains no reasoning, no recommendations, and no AI — only acquisition and
translation. Its vendor seam (`collector/sources/`) is built so the live Synopta source becomes
a **single new module**. See [`specs/gaia-collector.md`](../specs/gaia-collector.md) and
[`docs/gaia-collector.md`](../docs/gaia-collector.md).

### Edge Collector — the production scheduled-export bridge (Sprint 14)

[`collector/edge/`](../collector/edge/) is the unattended, all-day version of that bridge: it
watches a folder for a **scheduled Synopta export** (CSV/TSV/Excel/JSON), parses it into the same
raw vendor shape the translator already understands, and keeps `latest.json` current — with
content-hash dedup, partial-write/debounce protection, reboot & power-loss recovery, bounded safe
retries, a never-overwrite-newer freshness guard, durable Collector Health, and a Knowledge Gap
raised on failure. It is **purely additive** (the Brain, API, and Snapshot model are unchanged) and
its only remaining dependency is **Ridder enabling the scheduled export** — see
[`docs/ridder-synopta-export-specification.md`](../docs/ridder-synopta-export-specification.md) and
[`docs/sprint-14-go-live-checklist.md`](../docs/sprint-14-go-live-checklist.md).

## Conventions

- Every integration implements an internal interface defined in `specs/`. The
  rest of the application depends on the interface, never on the vendor.
- Provider-specific quirks (field names, units, auth, polling) are contained
  here and mapped into the [domain model](../domain/) at the boundary.
- Adding or replacing a provider must not require changes outside this folder and
  its configuration. If it does, the abstraction has leaked and needs fixing.
