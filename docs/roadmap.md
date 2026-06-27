# Roadmap

Direction, not fixed dates. The order reflects our principles: deliver real value
early, build trust before automation, and keep the Synopta swap friction-free.

## Sprint 0 — Foundation (current)

**Goal:** a professional engineering foundation before feature development.

- Repository structure and folder purpose.
- Core documentation: vision, architecture, project rules, roadmap, glossary.
- Domain Model v1.
- Founding ADRs (001–004).
- Greenhouse Provider specification.
- Architecture critique captured as RFC(s).
- Sprint 1 backlog.

**Exit criteria:** Sprint 0 reviewed and approved together. No application logic
or UI is built in Sprint 0.

## Sprint 1 — First live value (next)

**Goal:** Morning Intelligence delivering real value from live greenhouse data via
the Provider Layer.

Themes (broken into issues in the [Sprint 1 backlog](sprint-1-backlog.md)):

1. Implement the Greenhouse Provider interface and `ClaudeDispatchProvider`.
2. Represent the core Domain Model entities in code (no business rules yet).
3. Context Engine: assemble a minimal daily context.
4. Decision Engine: produce a first, narrow, explained recommendation.
5. Language Engine: render a calm Morning Intelligence briefing.
6. Memory: record decisions and outcomes (foundation for learning).

## Later

- **Replace `ClaudeDispatchProvider` with `SynoptaProvider`** with no change above
  the Provider Layer — the architecture's defining test.
- Broaden providers: Weather, Cameras, energy.
- Commerce and operations via Shopify (orders, customers, shipments) and Fortnox
  (finance, HR) — through providers.
- Close the learning loop so recommendations improve from outcomes.
- Hands-free interface (Even G2 glasses).

## Long-term goal

A trusted greenhouse intelligence that combines biological knowledge, continuous
learning, operational memory, and AI reasoning to support growers in real time —
the digital operating intelligence for Plant That Plant, and eventually for other
professional growers.
