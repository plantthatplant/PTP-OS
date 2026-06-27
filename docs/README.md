# docs/

Product and engineering documentation for PTP OS. These are the living,
high-level documents that describe *what* PTP OS is and *how* we build it.

| File | Purpose |
| --- | --- |
| [`vision.md`](vision.md) | Why PTP OS exists and what success looks like. |
| [`biological-model.md`](biological-model.md) | How PTP OS understands plants — a core design document. |
| [`decision-philosophy.md`](decision-philosophy.md) | How PTP OS should *think* — the reasoning constitution. A core design document. |
| [`cultivation-intelligence-model.md`](cultivation-intelligence-model.md) | How the world's best growers think — the biological foundation PTP OS inherits. A core design document. |
| [`daily-operating-cycle.md`](daily-operating-cycle.md) | How PTP OS thinks and acts across a whole day — the continuous biological decision loop. A core operating document. |
| [`gaia-learning-loop.md`](gaia-learning-loop.md) | How Gaia turns daily work into accumulated biological wisdom — recommendation → experiment → outcome → knowledge. A core design document. |
| [`gaia-first-day.md`](gaia-first-day.md) | Operational walkthrough — Gaia's complete first working day at Kålaberga, 06:00–18:00, using only existing components. (Not a core design doc.) |
| [`project-rules.md`](project-rules.md) | How we work: principles, engineering rules, and process. |
| [`architecture.md`](architecture.md) | How the system is structured and how data flows. |
| [`roadmap.md`](roadmap.md) | What we are building, in what order. |
| [`glossary.md`](glossary.md) | Shared project terminology. |
| [`repository-review.md`](repository-review.md) | Sprint 0 structure evaluation and rationale. |
| [`technical-health-report.md`](technical-health-report.md) | Chief-architect code review toward v1.0 — issues, subsystem scores, and the 500-greenhouse question. |
| [`sprint-1-backlog.md`](sprint-1-backlog.md) | Sprint 1 issues, ready for GitHub. |
| [`sprint-1-shortcuts.md`](sprint-1-shortcuts.md) | Every shortcut the first Greenhouse Brain takes, and what replaces it. |
| [`dispatch-runtime-investigation.md`](dispatch-runtime-investigation.md) | How Claude Dispatch actually communicates, and the cleanest integration point. |

## Conventions

- Documents here describe direction and structure, not implementation detail.
  Component-level behavior belongs in [`specs/`](../specs/); the rationale behind
  structural decisions belongs in [`adr/`](../adr/).
- Keep these documents current. When an ADR changes the architecture, update
  `architecture.md` and link the ADR.
- Write in plain language. A grower or a new engineer should both be able to
  follow the vision and rules.
