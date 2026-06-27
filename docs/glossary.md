# Glossary

Shared vocabulary for PTP OS. When a term has a precise meaning in this project,
it is defined here. Domain entities have their own detailed pages in
[`domain/`](../domain/); this glossary is the quick reference.

## System & architecture

- **PTP OS** — The AI-native operating system for professional greenhouse
  production described in this repository.
- **Provider Layer** — The boundary through which every external system enters PTP
  OS. Maps external data into the Domain Model.
- **Provider** — A component that implements a provider interface for one external
  system (e.g. `ClaudeDispatchProvider`, `SynoptaProvider`).
- **Context Engine** — Service that assembles the relevant current picture of the
  greenhouse.
- **Decision Engine** — Service that reasons over context to produce
  recommendations with rationale. Decides; does not phrase.
- **Language Engine** — Service that renders structured decisions into calm, clear
  language. Phrases; does not decide.
- **Memory Engine** — Service that retains experience and links decisions to
  outcomes so the system learns.
- **Decision Library** — Catalog of decision types and their structure.
- **Domain Model** — The set of entities the system reasons about; the shared
  vocabulary. See [`domain/`](../domain/).
- **Morning Intelligence** — The default interface: the daily briefing that
  delivers value to the grower.

## Process & documents

- **ADR (Architecture Decision Record)** — An immutable record of one significant
  decision: context, decision, consequences, alternatives. See [`adr/`](../adr/).
- **RFC (Request for Comments)** — A proposal to change the architecture, reviewed
  before adoption: current design, proposal, benefits, risks, migration. See
  [`rfc/`](../rfc/).
- **Spec (Specification)** — A document describing how a component must behave,
  written and agreed before implementation. See [`specs/`](../specs/).
- **One prompt = one feature** — Principle that each AI-backed capability is a
  single, versioned prompt.

## Domain terms (summary — see `domain/` for detail)

- **Greenhouse** — A physical growing facility.
- **Zone** — A controllable sub-area within a greenhouse.
- **Bench** — A physical growing surface within a zone where plants are placed.
- **Plant** — A single cultivated plant.
- **Plant Batch** — A group of plants managed together as one unit.
- **Mother Plant** — A plant kept as a source of cuttings/propagation material.
- **Species** — The botanical type of a plant, with its cultivation
  characteristics.
- **Observation** — A recorded fact about reality at a point in time.
- **Climate Reading** — A measured environmental value (temperature, humidity,
  CO₂, light, etc.); a specialized observation.
- **Recommendation** — A suggested action produced by reasoning, with explanation.
- **Decision** — What was actually decided and done (or deliberately not done).
- **Memory** — Retained experience linking decisions to outcomes.
- **Task** — A unit of work to be carried out, often arising from a decision.
- **Employee** — A person who works in the operation.
- **Customer** — A buyer of the operation's plants.
- **Order** — A customer's purchase request.
- **Shipment** — The fulfilment/dispatch of an order.
- **Weather** — External meteorological conditions affecting the greenhouse.
- **Energy Event** — A noteworthy change in energy use, cost, or supply.

## Future integrations

- **Claude Dispatch** — Initial greenhouse data provider.
- **Synopta** — Long-term greenhouse data source (Synopta Pro/API), replacing
  Claude Dispatch behind the Provider Layer.
- **Shopify** — Future provider for commerce (orders, customers).
- **Fortnox** — Future provider for finance and HR.
- **Even G2 glasses** — Future hands-free primary interface.
