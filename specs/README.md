# specs/

Technical specifications for PTP OS components.

**Every feature has a specification before it is implemented.** A spec describes
how a component must behave — its responsibilities, interface, inputs and
outputs, error handling, and how it accommodates the future Synopta integration —
without prescribing throwaway implementation detail.

| Spec | Describes |
| --- | --- |
| [`greenhouse-snapshot.md`](greenhouse-snapshot.md) | The canonical, source-agnostic structure every data acquisition method produces — reality at a moment in time. |
| [`greenhouse-provider.md`](greenhouse-provider.md) | The Provider interface and the ClaudeDispatchProvider → SynoptaProvider swap path. |
| [`greenhouse-brain-v1.md`](greenhouse-brain-v1.md) | The reasoning pipeline from question to answer for "How is the greenhouse today?" — the blueprint for the first Greenhouse Brain. |
| [`first-useful-decision.md`](first-useful-decision.md) | The reasoning process for "What should I do during the next two hours?" — the first operational workflow, ranked for long-term plant health. |
| [`decision-capture.md`](decision-capture.md) | How PTP OS captures expert grower reasoning as learning material — the foundation for continuous learning. |
| [`daily-grower-dialogue.md`](daily-grower-dialogue.md) | The daily two-way conversation through which Gaia and the Head Grower improve together. |
| [`decision-library.md`](decision-library.md) | Gaia's accumulated biological experience — every recommendation becomes a queryable decision record. The long-term memory. |
| [`curiosity-engine.md`](curiosity-engine.md) | How Gaia begins asking — searching for unusual, unexplained, or interesting patterns and forming hypotheses (never alarms). |
| [`knowledge-gap-engine.md`](knowledge-gap-engine.md) | The Value-of-Information rule for asking only the few questions whose answers would change a decision. |
| [`gaia-collector.md`](gaia-collector.md) | The local Synopta → Canonical Snapshot bridge (the first real acquisition component). |
| [`field-companion.md`](field-companion.md) | Gaia's device-independent presence on a greenhouse walk — when to speak, when to stay silent. |
| [`observer-network.md`](observer-network.md) | The Observer Network concepts — how Gaia observes reality through interchangeable observers. |
| [`observation-planner.md`](observation-planner.md) | Gaia's active-perception engine — deciding which observation is worth making, by whom, when, or not at all. |

## What a spec should contain

1. **Purpose** — what problem this component solves.
2. **Scope** — what is in and explicitly out.
3. **Interface / contract** — the boundary other code depends on.
4. **Behavior** — inputs, outputs, error and edge cases.
5. **Future integrations** — how it accommodates Synopta and other future change.
6. **Open questions** — anything unresolved, so it is reviewed rather than guessed.

## Conventions

- One spec per component or capability.
- A spec is reviewed and agreed before implementation begins.
- When a spec changes, note the change and the date at the top of the file.
- Interfaces in specs are illustrative contracts, not final code. The
  implementation language is decided per the roadmap, not assumed here.
