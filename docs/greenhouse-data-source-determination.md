# Greenhouse Data Source — Determination (Sprint 4)

**Date:** 2026-06-27 · **Question:** where do the greenhouse values Claude can report
("what is the temperature right now?") actually originate, and is there an officially supported
source Gaia should consume? · **Method:** inspected the tools/connectors available to this
Claude session and the provenance of every value used so far; researched Ridder/Synopta's
public product/API surface. No reverse engineering. Facts and assumptions are tagged.

---

## 1. Headline finding (important, and against the premise)

**In this environment, Claude is not reading any live greenhouse source. Every greenhouse
value it has produced comes from mock/fixture files committed in this repository.** There is no
Synopta Cloud connection, no Ridder API, and no greenhouse data tool wired to this session.

This needs to be said plainly because the sprint premise assumes a live source already exists.
The honest evidence says otherwise (§2). An officially supported source *does exist at the
vendor level* (§3), but **it is not what Claude is currently reading**, and access to it cannot
be established from the evidence available here (§5).

---

## 2. Where the values actually originate — [FACT]

- **No greenhouse/Synopta/Ridder data tool is connected to this Claude session.** A capability
  search returned nothing; the MCP connector registry has **no** Synopta/Ridder/HortiMaX/
  greenhouse connector. [FACT, high]
- **Every "temperature/humidity/…" value Claude has shown traces to repository fixtures:**
  `app/sample_snapshot.json`, `collector/sources/sample_synopta_export.json`,
  `app/greenhouse_brain/providers/sample_claude_dispatch.json`, and `app/demo/*.json` — each
  explicitly labelled a stand-in (e.g. *"Stands in for a real live-observation file — none was
  provided"*). [FACT, high]
- Therefore the answer "the temperature is 24.2 °C" is a **mock value**, not a live reading.
  [FACT, high]

> If anyone has seen Claude report a *real* current value, that would have happened in a
> different context (e.g. a person reading the Synopta desktop/mobile app, or Claude reading a
> screen) — which is **screen reading, not an officially supported data source**, and there is
> no evidence of it in this environment. We do not assume it. [stated to avoid a false premise]

---

## 3. Does an officially supported source exist? — [FACT from public info]

Yes, at the vendor level:

- **Synopta is Ridder/Hortimax supervision software** with **desktop + mobile app + remote/
  cloud access** ("always connected", monitor/adjust "from anywhere"). A mobile app implies a
  **Ridder backend service that serves greenhouse data** to it. [FACT, web]
- Ridder markets **"HortOS API services"** and a customer **portal at `portal.ridder.com`**
  ("Connected systems, data, and AI"). [FACT, web]
- Consistent with this installation: Sprint 3 found this PC already uses the **Ridder portal**
  (the CX Assistant's `PortalDLL` downloads `.site` config over HTTPS) and the controller
  definitions include **`SynHortOS.dat`** — i.e. the site is already in the HortOS/portal
  ecosystem. [FACT, this machine]

So the *officially supported source* that could provide live data is the **Ridder HortOS /
Synopta cloud (portal.ridder.com)** — a vendor service, reached over the internet, **not**
anything currently connected to Claude or hosted on the local machine.

Note: **"Ridder iQ API"** seen in search results is Ridder's **ERP** product (manufacturing/
accounting), **not** the greenhouse climate system — a different product line. Do not conflate
them. [FACT, web]

---

## 4. Authenticated access & documentation — [ASSUMPTION / UNKNOWN]

- **Public API documentation, endpoints, and auth details are not available** from open
  sources; Ridder's pages point to the portal / "contact us" rather than published developer
  docs. [FACT, web]
- Whether the HortOS/Synopta cloud API **exposes this specific Kålaberga (HortiMaX CX) site's**
  live and historical climate data, and whether **read-only credentials** can be provisioned,
  is **not determinable from available evidence.** [ASSUMPTION — requires Ridder]

---

## 5. Decision: STOP — the source exists, but access is not determinable here

The officially supported source is identifiable (Ridder HortOS / Synopta cloud), but **its
access specifics cannot be determined from the evidence available in this environment**, and the
sprint forbids guessing. So we stop and state exactly what external information is required.

### External information required (to be obtained from Ridder)
1. **Confirmation** that the Ridder HortOS / Synopta cloud API exposes **this site's** live (and
   historical) climate data — for the Kålaberga HortiMaX CX controller. The site is likely
   identified by the controller serial **`269221677002BQ`** and/or the local site GUID
   **`A8301A54-DA1D-427E-895C-E25BD788F235`** (both observed on this machine).
2. **API documentation:** base URL, endpoints, the data schema, **units**, and **update
   cadence** for each measurement.
3. **Authentication method** and **read-only credentials / API key** scoped to this site.
4. **Terms:** confirmation of read-only scope, rate limits, and acceptable use.

These four items are the entire gate. None can be safely inferred; all come from Ridder (or the
account owner via `portal.ridder.com`).

---

## 6. Recommendation — how Gaia consumes it, preserving the Provider architecture

Once the four items above are in hand, the integration is **one new module**, exactly as the
existing architecture anticipates — nothing above the seam changes:

- Implement **`HortOSApiSource`** (a `SynoptaSource`) in `collector/sources/` that calls the
  Ridder HortOS API read-only, with credentials taken from environment variables (never
  committed), and returns the raw payload.
- Register it in `make_source` (e.g. `--source hortos-api`).
- Confirm/adjust the field mapping in `collector/translate.py` against a captured real payload;
  add it as a fixture + translation test.
- The Collector then emits a **Canonical Snapshot** to `data/inbox/latest.json`, which the Brain
  consumes through `SnapshotProvider` **unchanged**.

This keeps the defining constraint intact: *greenhouse data enters only through the Provider
Layer, and the value outlives any source.* The cloud API simply becomes one more source behind
the seam — and the first that is *real*.

---

## 7. Facts vs assumptions (at a glance)

**Facts:** no greenhouse data tool/connector is wired to this Claude session; all values shown
so far are repo fixtures; Synopta has an official desktop/mobile/cloud product; Ridder markets
"HortOS API services" + `portal.ridder.com`; this site already uses the Ridder portal; "Ridder
iQ API" is a separate ERP product.

**Assumptions (need Ridder to confirm):** that the HortOS/Synopta cloud API exposes this site's
climate data; that read-only credentials and documentation can be provisioned; the exact
endpoints, schema, units, and cadence.

**Sources:** Ridder product/cloud pages and search results for Synopta/HortOS (see the chat
message accompanying this report for the specific URLs).
