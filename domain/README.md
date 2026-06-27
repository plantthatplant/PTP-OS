# domain/

The **domain model** of PTP OS: the concepts the system reasons about, expressed
in the language growers and engineers share. This vocabulary is what the Context,
Decision, and Language engines all operate on.

The domain model is **independent of any AI model and of any data provider**.
Entities describe greenhouse reality, not how a particular provider returns it.
This is what lets us swap Claude Dispatch for Synopta — and later add Shopify,
Fortnox, Weather, Cameras — without touching business logic. See
[ADR-002](../adr/ADR-002-provider-abstraction.md) and
[ADR-003](../adr/ADR-003-business-logic-independent-from-ai.md).

## Entities (v1)

Physical structure

| Entity | Purpose |
| --- | --- |
| [`greenhouse.md`](greenhouse.md) | The physical growing facility. |
| [`zone.md`](zone.md) | A controllable sub-area within a greenhouse. |
| [`bench.md`](bench.md) | A growing surface within a zone where plants sit. |

Living things

| Entity | Purpose |
| --- | --- |
| [`plant.md`](plant.md) | A single cultivated plant. |
| [`plant-batch.md`](plant-batch.md) | A group of plants managed as one unit. |
| [`mother-plant.md`](mother-plant.md) | A plant kept as a source of propagation material. |
| [`species.md`](species.md) | The botanical type and its cultivation characteristics. |

Sensing & reasoning

| Entity | Purpose |
| --- | --- |
| [`observation.md`](observation.md) | A recorded fact about reality at a point in time. |
| [`climate-reading.md`](climate-reading.md) | A measured environmental value; a specialized observation. |
| [`recommendation.md`](recommendation.md) | A suggested action with explanation. |
| [`decision.md`](decision.md) | What was actually decided and done. |
| [`memory.md`](memory.md) | Retained experience linking decisions to outcomes. |

Operations & people

| Entity | Purpose |
| --- | --- |
| [`task.md`](task.md) | A unit of work to be carried out. |
| [`employee.md`](employee.md) | A person who works in the operation. |

Commerce

| Entity | Purpose |
| --- | --- |
| [`customer.md`](customer.md) | A buyer of the operation's plants. |
| [`order.md`](order.md) | A customer's purchase request. |
| [`shipment.md`](shipment.md) | The fulfilment/dispatch of an order. |

Environment & resources

| Entity | Purpose |
| --- | --- |
| [`weather.md`](weather.md) | External meteorological conditions. |
| [`energy-event.md`](energy-event.md) | A noteworthy change in energy use, cost, or supply. |

## Documentation format

Each entity is documented with the same five sections, so the model stays
consistent and reviewable:

- **Purpose** — what the entity represents and why it exists.
- **Relationships** — how it connects to other entities.
- **Important properties** — the key attributes (v1, conceptual, non-exhaustive).
- **Future integrations** — how it maps to Synopta, Shopify, Fortnox, Weather,
  Cameras, etc.
- **Examples** — concrete instances to make the concept tangible.

## Conventions

- This is **v1**. The model will evolve deliberately and changes are documented.
- Properties are conceptual, not a database schema. Storage and types are decided
  when the relevant component is specified and built.
- Provider-specific fields stay out of the domain. Mapping from a provider's shape
  into these entities happens in the Provider Layer.
