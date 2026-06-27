# Shipment

## Purpose
The fulfilment and dispatch of an **Order** — the physical movement of finished
plants out of the greenhouse to a customer. Shipments close the production-to-
delivery loop and free up space and inventory.

## Relationships
- Fulfils one (or part of one) **Order**.
- Draws specific **Plants** / from **Plant Batches**.
- Departs a **Greenhouse**; carried out via **Tasks** by **Employees**.

## Important properties
- Identity: stable id.
- Order reference and customer.
- Contents: which plants/batches and quantities.
- Dispatch date, carrier/method, destination.
- Status (planned, packed, shipped, delivered).

## Future integrations
- **Shopify** — fulfilment status sync via a provider.
- **Fortnox** — delivery may trigger invoicing.
- **Weather** — extreme conditions can affect shipping decisions for live plants.

## Examples
- "Shipment SH-2026-0312: 80 Monstera from Batch MD-2026-014, shipped 2026-07-09
  to Plantagen via refrigerated carrier."
- A partial shipment covering half of a large order, with the remainder to follow.
