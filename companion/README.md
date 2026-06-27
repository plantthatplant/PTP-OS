# Gaia Field Companion

Gaia's **device-independent presence in the greenhouse**. It decides, while the grower walks,
**when to speak and when to stay silent** — using only what the engines already produced. It
performs **no biological reasoning** and depends on **no device**.

Spec: [`specs/field-companion.md`](../specs/field-companion.md) ·
Founder review: [`docs/field-companion-founder-review.md`](../docs/field-companion-founder-review.md)

```
Gaia engines ─▶ Interaction Engine ─▶ CompanionDisplay (8 primitives) ─▶ device adapter
(VoI questions,   (ask here/now? or     (device-independent)              (Even G2 today;
 priorities,       silence — EVI vs                                        Android, AR, voice,
 confidence)       context cost)                                           robot tomorrow)
```

## Run the demonstration

```
python companion/demo_walk.py                       # one full walk on a simulated Even G2
python -m unittest discover -s companion/tests      # the tests
```

The walk: Morning Brief → silence → one biologically valuable question → grower answers →
confidence updates → memory updates → silence → Evening Review → learning.

## What it is — and never does

- **Consumes Gaia only.** Reads Morning Analysis, Knowledge-Gap Questions (already VoI-scored),
  open Experiments, the Snapshot. **No biology, no new reasoning.**
- **Silence is the default.** Speaks only when expected biological value **>** context-aware
  interruption cost. Reuses `knowledge_gap` (VoI), `workflow` (timing/location/`interrupt_now`),
  `lifecycle` (`reinforce`/confidence), `store` (memory + learning).
- **Device-independent.** The Brain never imports the Companion; the Companion never imports a
  device. Both are enforced by tests.

## The eight device-independent primitives

`show_message · show_priority · show_question · show_status · show_navigation ·
show_confirmation · show_warning · show_summary` — each takes a small `CompanionMessage`
(headline ≤ 40 chars, optional short detail, urgency, tiny fixed answer set). A device adapter
translates them; **EvenG2Display** renders one line to the HUD, **ConsoleDisplay** to a terminal.

## Files

| Path | Role |
| --- | --- |
| `interaction_engine.py` | Choose the next interruption or silence; build + store the `InteractionRecord`. |
| `walk.py` | `WalkSession` — composes engine + analysis + display into the interaction modes; chooses wording. |
| `display.py` | `CompanionDisplay` — the device-independent interface (8 primitives). |
| `messages.py` | `CompanionMessage`, `Mode`, `Urgency`, `Primitive`. |
| `devices/even_g2.py` | Even G2 HUD adapter (one line; the only live-device gap is `_send_to_device`). |
| `devices/console.py` | Terminal adapter (development). |
| `demo_walk.py` | The end-to-end walk demonstration. |
| `tests/` | Economics (silence/EVI/spacing), record completeness, device-independence. |

## Adding a device

Implement `render()` (and optionally `ask()`) in a new `devices/<name>.py`. Nothing above it
changes — the Interaction Engine, the modes, and the Brain are untouched. Even G2's only
remaining piece for real hardware is the SDK transport in `EvenG2Display._send_to_device`.

## Interaction modes

`MORNING_WALK · INSPECTION · KNOWLEDGE_GAP · OBSERVATION_CONFIRMATION · ALERT · NAVIGATION ·
SILENT_MONITORING · EVENING_REVIEW`. A mode selects which primitive/flow applies; it adds no
biology.
