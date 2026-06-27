# Spec — Greenhouse Provider

**Status:** Draft v1 · Sprint 0 (for review before implementation)
**Related:** [ADR-002](../adr/ADR-002-provider-abstraction.md),
[ADR-003](../adr/ADR-003-business-logic-independent-from-ai.md),
[`integrations/`](../integrations/), [`domain/`](../domain/)

> The interface below is an **illustrative contract** expressed in TypeScript-like
> pseudocode for clarity. It is not a commitment to a language or to final
> signatures — the implementation stack is decided in Sprint 1. What is being
> agreed here is the *shape and behavior* of the boundary, not the syntax.

## 1. Purpose
Define the single boundary through which PTP OS obtains its view of greenhouse
reality. The rest of the system asks "what is happening in the greenhouse?" and
receives answers **as the [Domain Model](../domain/)** — with no knowledge of which
vendor produced them.

This boundary exists so that `ClaudeDispatchProvider` (today) can be replaced by
`SynoptaProvider` (later) **without changing anything above the Provider Layer**.

## 2. Scope
**In scope:** read access to greenhouse structure and conditions — greenhouses,
zones, benches, climate readings, and other observations sourced from the
greenhouse data system.

**Out of scope (v1):** writing back / actuating controls; commerce, finance,
weather, and camera data (each gets its own provider later — see
[`rfc/RFC-002-provider-taxonomy.md`](../rfc/RFC-002-provider-taxonomy.md)).

## 3. The contract

```ts
// All return types are Domain Model types (see domain/). No vendor types leak out.

interface GreenhouseProvider {
  // Identity & capability
  readonly name: string;                       // e.g. "claude-dispatch", "synopta"
  capabilities(): ProviderCapabilities;        // what this provider can supply

  // Structure
  getGreenhouses(): Promise<Greenhouse[]>;
  getZones(greenhouseId: Id): Promise<Zone[]>;
  getBenches(zoneId: Id): Promise<Bench[]>;

  // Conditions
  getLatestClimate(query: ClimateQuery): Promise<ClimateReading[]>;
  getClimateHistory(query: ClimateHistoryQuery): Promise<ClimateReading[]>;
  getObservations(query: ObservationQuery): Promise<Observation[]>;

  // Liveness
  healthCheck(): Promise<ProviderHealth>;
}

interface ProviderCapabilities {
  supportsHistory: boolean;
  supportedMetrics: ClimateMetric[];           // temperature, humidity, co2, light, ...
  minSampleInterval?: Duration;                // finest resolution available
}

type ClimateQuery = { scope: LocationRef; metrics?: ClimateMetric[] };
type ClimateHistoryQuery = ClimateQuery & { from: Timestamp; to: Timestamp };
type ObservationQuery = { scope: LocationRef; types?: ObservationType[]; since?: Timestamp };
type LocationRef = { greenhouseId: Id; zoneId?: Id; benchId?: Id };
```

### Contract rules
- **Domain types only.** Inputs and outputs use domain types and identifiers.
  Vendor field names, units, and payloads never cross this boundary.
- **Stable identifiers.** Providers map vendor ids to stable PTP OS ids and keep
  that mapping internal.
- **Units are normalized** to the domain's canonical units (e.g. °C, %RH, ppm,
  µmol·m⁻²·s⁻¹). Conversion happens inside the provider.
- **Read-only in v1.** No method mutates greenhouse state.
- **Capabilities are explicit.** Callers check `capabilities()` rather than
  assuming; a provider that lacks history says so instead of failing obscurely.

## 4. Behavior

- **Inputs:** location-scoped queries; optional metric/type filters and time
  ranges.
- **Outputs:** arrays of domain entities; empty array (not error) when there is
  simply no data.
- **Errors:** a small, provider-neutral error taxonomy —
  `ProviderUnavailable`, `NotSupported` (capability absent), `InvalidQuery`,
  `AuthError`. Vendor-specific errors are translated into these. Callers never see
  a raw vendor error.
- **Time:** all timestamps normalized to UTC at the boundary.
- **Missing/late data:** readings carry their own `timestamp` and `source`/
  `confidence`; gaps are represented as absence, not as fabricated values.
- **Configuration:** a provider is selected and configured at composition time
  (e.g. via configuration/dependency injection), never chosen inside business
  logic.

## 5. Swapping Claude Dispatch → Synopta

The whole point of this spec. The swap is a **composition change**, not a code
change in the core.

```
        ┌────────────────────────────────────────────┐
        │  Context Engine / Decision Engine / …        │  ← unchanged
        └───────────────────────┬──────────────────────┘
                                │ depends on GreenhouseProvider (interface)
                                ▼
        ┌──────────────────────────────────────────────┐
        │              Provider Layer                    │
        │  today:   ClaudeDispatchProvider               │
        │  later:   SynoptaProvider  (Synopta Pro/API)   │
        └──────────────────────────────────────────────┘
```

Migration steps when Synopta is ready:
1. Implement `SynoptaProvider` against this same interface; contain all
   Synopta-specific auth, endpoints, field mapping, and unit conversion inside it.
2. Validate it against the shared **provider conformance tests** (Section 6).
3. Optionally run both in parallel (shadow mode) and compare outputs on live data
   to build trust before switching.
4. Change configuration to select `SynoptaProvider`. Decommission Claude Dispatch.

No change is required in the Context Engine, Decision Engine, Language Engine,
Memory, or the domain model. If any such change *is* required, the abstraction has
leaked and must be fixed rather than worked around.

## 6. Provider conformance tests
A single shared test suite defines what it means to be a valid
`GreenhouseProvider`. Every provider (Claude Dispatch, Synopta, and any fake used
in development) must pass it. This is how we guarantee substitutability rather than
merely hoping for it. The suite covers: domain-type/unit correctness, capability
honesty, error-taxonomy mapping, time normalization, and empty-vs-error behavior.

## 7. Future integrations
- **Synopta** is the immediate target of this interface.
- Other domains (Weather, Cameras, Shopify, Fortnox, energy) follow the same
  *pattern* but are **separate provider interfaces**, since their data and
  semantics differ from greenhouse climate. The general taxonomy is proposed in
  [`rfc/RFC-002-provider-taxonomy.md`](../rfc/RFC-002-provider-taxonomy.md).
- **Write/actuation** (adjusting setpoints) is a deliberate future extension and
  will be specified separately, gated by the "trust before automation" principle.

## 8. Open questions
1. Streaming vs. polling for live climate — does Synopta push or must we pull?
   (Affects whether a subscription method is added later.)
2. Exact canonical unit and metric list — to be fixed with the first real data.
3. Identifier strategy for mapping vendor ids to stable PTP OS ids.
4. How far back history must be available for Memory/learning needs.

These are listed so they are resolved in review, not assumed.
