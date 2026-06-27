# Customer

## Purpose
A buyer of the operation's plants — typically a retailer, wholesaler, or
direct buyer. Customers connect production to demand, letting PTP OS reason about
what to grow and when plants are needed.

## Relationships
- Places **Orders**.
- Orders are fulfilled by **Shipments** drawn from **Plant Batches**.

## Important properties
- Identity: stable id, name.
- Type (retail, wholesale, direct).
- Contact and delivery details.
- Commercial terms (where relevant).
- History summary (for demand context).

## Future integrations
- **Shopify** — authoritative source of customers via a provider; PTP OS mirrors
  only the operational view it needs.
- **Fortnox** — invoicing/financial relationship.

## Examples
- "Plantagen — wholesale customer, weekly standing order."
- A direct B2B customer ordering finished Monstera in bulk for an event.
