# Investigation — How Claude Dispatch Actually Communicates

**Status:** Findings · investigation only (no code added, no reasoning changed).
**Date:** 2026-06-27.

A read-only investigation of this machine to determine how "Claude Dispatch" runs and
where it gets greenhouse data, so we can pick the cleanest, least-invasive integration
point. Method: inspected running processes, listening TCP ports, the Claude Desktop MCP
config, the project tree, and on-disk config/credentials.

## The headline finding

**There is no "Claude Dispatch" runtime on this machine.** No process, no listening
port, no MCP server, no config entry, and no credentials reference it. The term appears
in exactly one place: **our own PTP-OS project** (the vision/ADR docs and the code we
wrote). "Claude Dispatch" is a *name we chose* for "use Claude to obtain Synopta data" —
not a discovered product with an API to connect to.

The only Claude runtime present is the **Claude Desktop app** (`/Applications/Claude.app`,
`com.anthropic.claudefordesktop`, v1.14271.0) — i.e. this app, running in Cowork/local-
agent mode. It ships a Chrome-extension native host (Claude-in-Chrome) and has
computer-use enabled. It exposes **no local TCP API** of its own.

## Answers to the specific questions

- **Does Claude Dispatch expose an HTTP endpoint?** Not locally — none found. If "Dispatch"
  is meant to be the Synopta cloud, *Synopta* may expose an API, but nothing on this
  machine does, and that is unverified from here.
- **Does it communicate over WebSockets?** No local WebSocket server attributable to
  Dispatch/Synopta was found.
- **Is there a local process exposing an API?** No. The only listeners on the box are
  unrelated system/app services (rapportd, ControlCenter/AirPlay on :5000/:7000, Adobe CC,
  Spotify, Dropbox). Claude Desktop itself was not listening on any port.
- **Can the current Dispatch session be reused by Claude Code?** There is no separate
  "Dispatch session" to reuse — the only session is this Claude (Desktop/Cowork) runtime.
  If "Dispatch" means *Claude extracting Synopta via the browser/computer-use*, then the
  same runtime can do that work (so it is "reused" only in the sense that one agent does
  both jobs). There is no API session or token to hand off to a separate Claude Code CLI;
  a CLI surface would not inherit the Desktop browser session automatically.
- **Where does Dispatch obtain its greenhouse data?** Not determinable on this machine.
  Background (external knowledge, to confirm): Synopta is Hoogendoorn's greenhouse
  management system; its data lives in the in-greenhouse climate computer and the Synopta
  cloud portal, reachable via a web UI and possibly an official API. Today, in our
  prototype, the data origin is the captured fixture / the local stand-in endpoint — both
  ours.
- **Which part of the current implementation can be replaced by a real transport with the
  smallest possible change?** Exactly one seam: **`DispatchTransport.fetch() -> dict`**
  (`app/greenhouse_brain/providers/transport.py`). Everything above it — the
  ClaudeDispatchProvider translation, the domain model, and all four engines — stays
  untouched. The integration is "implement/point one transport." Nothing else moves.

## The cleanest integration point

We already built the right seam. The only thing the system needs is a `fetch()` that
returns the raw payload dict:

```
        (wherever the data really comes from)
                       │
                       ▼
        DispatchTransport.fetch() -> raw dict     <-- the ONLY thing that changes
                       │
                       ▼
        ClaudeDispatchProvider  (translation — unchanged)
                       ▼
        Domain Model -> Context -> Decision -> Morning Analysis  (untouched)
```

## Recommended least-invasive strategy

Decide based on one unknown only you can confirm — **does Synopta expose a usable API?**

1. **If Synopta (or a Hoogendoorn) API exists → use the transport we already have.**
   Point `HttpDispatchTransport` at it and add the API key:
   `PTP_PROVIDER=claude-dispatch PTP_DISPATCH_URL=… PTP_DISPATCH_KEY=…`. **Near-zero code**
   — only a mapping tweak inside the provider if the API's shape differs from our payload.
   This is the cleanest of all *if* the API is real.

2. **If there is no API (portal only) → a file-drop bridge is the smallest change of all.**
   A scheduled Claude job (Claude-in-Chrome / computer-use) reads the Synopta portal,
   extracts the 7 signals, and writes them as our raw payload JSON to a known path. The
   Brain consumes it via `FixtureTransport(path=<that file>)` — which **already accepts a
   path**, so this needs *no new application code*: just a scheduled extraction and a
   config pointer. It also cleanly separates "getting data" (an agent's job, where the
   live messiness lives) from "reasoning" (the Brain), and the Brain stays unaware. This
   *is* "Claude Dispatch" in the literal sense — Claude dispatching the data.

3. **Only if a push/realtime feed is needed later:** a small long-running bridge that holds
   the latest snapshot and serves it over HTTP (what our demo server imitates) or a
   WebSocket transport. More moving parts; not warranted yet.

**Recommendation:** confirm the API question first. Absent a confirmed API, go with
**option 2 (file-drop bridge)** — it is the least invasive (no new code, reuses
`FixtureTransport`), the most robust (extraction failures never reach the Brain), and the
truest to the architecture (the transport seam absorbs all the messiness). Promote to
option 1 the moment a real API is in hand.

## What only you can confirm (open questions)

1. Is "Claude Dispatch" an external service you already operate, or — as the evidence
   here suggests — a *name in our design* for Claude-driven extraction?
2. Does Synopta expose an API (REST/other) with credentials we can use? If so, its base
   URL and auth method decide option 1 immediately.
3. If portal-only: what is the portal URL, and is a logged-in browser session available
   for a scheduled Claude job to read?
4. How fresh must the data be (every morning is enough? near-real-time?) — this is the
   only thing that would push us from option 2 toward option 3.
