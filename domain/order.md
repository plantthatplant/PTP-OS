# Order

## Purpose
A **Customer's** purchase request for plants. Orders are the demand signal: they
tell PTP OS what must be ready, in what quantity, and by when — linking commerce
back to production planning.

## Relationships
- Placed by a **Customer**.
- Fulfilled from finished **Plants** / **Plant Batches**.
- Realized by one or more **Shipments**.
- May influence **Recommendations** and **Tasks** (e.g. prioritize a batch).

## Important properties
- Identity: stable id, order number.
- Customer reference.
- Line items: species/product, quantity, required size/quality.
- Required/promised date.
- Status (open, reserved, fulfilled, cancelled).

## Future integrations
- **Shopify** — authoritative source of orders via a provider; PTP OS keeps the
  operational view needed for planning and fulfilment.
- **Fortnox** — invoicing once fulfilled.

## Examples
- "Order #10472: 80 finished Monstera, size 17 cm, needed 2026-07-10, for
  Plantagen."
- A direct order reserved against Batch MD-2026-014.
