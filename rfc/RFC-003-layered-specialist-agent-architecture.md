# RFC-003 — Layered architecture: specialist agents as consumers of one reasoning core

**Status:** Open · raised in Sprint 0 (architecture reconciliation)
**Related:** [`docs/architecture.md`](../docs/architecture.md),
[ADR-001](../adr/ADR-001-separate-reasoning-from-language-generation.md),
[ADR-003](../adr/ADR-003-business-logic-independent-from-ai.md),
[RFC-001](RFC-001-feedback-and-learning-loop.md),
[`docs/biological-model.md`](../docs/biological-model.md)

## Context / the critique

Two architectural pictures of PTP OS exist in our own material, and they appear to
disagree:

1. The **committed architecture** ([`docs/architecture.md`](../docs/architecture.md))
   is a single, linear reasoning pipeline:
   `Reality → Provider → Context → Decision → Language → User`, with AI confined to
   the Language Engine and business logic independent of any model (ADR-003).
2. The **founding product vision** (the Agent Handbook, the Technical Blueprint)
   describes a *company of specialists* — an **AI COO** coordinating roughly a dozen
   domain agents (Climate Keeper, Plant Biologist, Plant Doctor, Energy Optimizer,
   Production Planner, Inventory Manager, Shipping Coordinator, Customer Success,
   Finance Partner, Operations Coordinator, Learning Engine).

Read naively, these look like competing architectures: one brain vs. many brains.
Left unreconciled, the risk is real and expensive — either the specialist vision
quietly mutates the clean pipeline into a dozen independent, model-entangled
mini-reasoners (each with its own logic, prompts, and notion of "stress" or
"confidence"), or the specialist vision is dropped and the product loses the
organising idea that makes it legible to growers.

**This RFC resolves the apparent conflict.** The linear pipeline is *not* replaced
by agents. The pipeline **is the core intelligence**. Specialist agents are
**consumers** of that core — bounded lenses onto the same Context and Decision
Engines — not replacements for them. There is **one brain; the specialists are
roles it plays**, not separate minds. This is a documentation/model change that
makes an already-intended structure first-class; it introduces no new product
behaviour and no implementation.

## Current design

- One linear pipeline (Context → Decision → Language) plus supporting services
  (Memory Engine, Decision Library, Knowledge Platform, Morning Intelligence).
- The **specialist agents have no place in the architecture document at all.** They
  live only in product/vision docs, with no stated relationship to the engines.
- Consequence: nothing says whether an "agent" is a separate reasoner, a
  configuration of the shared one, or merely a UI grouping. That ambiguity is what
  invites duplicated intelligence.

## Proposed improvement

Adopt an explicit **three-layer architecture**. The existing pipeline becomes the
middle of three named layers; agents and interfaces are the layers around it.

```
┌─────────────────────────────────────────────────────────────────────┐
│  USER INTERFACES LAYER                                                │
│  Morning Intelligence · conversational follow-up · Even G2 glasses    │
│  (renders structured output; assumes no screen)                       │
└───────────────────────────────▲───────────────────────────────────────┘
                                │  structured recommendations / briefings
┌───────────────────────────────┴───────────────────────────────────────┐
│  SPECIALIST AGENTS LAYER                                               │
│                                                                       │
│        AI COO  (orchestrator: prioritise, deduplicate, resolve)       │
│      ┌────────┬────────┬────────┬────────┬────────┬────────┐          │
│   Climate  Plant   Plant   Energy   Prod.   ...   Learning            │
│   Keeper  Biologist Doctor Optimizer Planner      Engine              │
│                                                                       │
│  Each agent = a SCOPE + a set of decision types + an objective slice. │
│  Agents hold NO reasoning of their own and NO model dependency.       │
└───────────────────────────────▲───────────────────────────────────────┘
                                │  scoped context queries / decision requests
┌───────────────────────────────┴───────────────────────────────────────┐
│  CORE INTELLIGENCE LAYER  (the one brain — the existing pipeline)      │
│                                                                       │
│  Provider Layer → Context Engine → Decision Engine → Language Engine   │
│  Supporting: Memory Engine · Decision Library · Knowledge Platform     │
│                                                                       │
│  Reasoning, the Biological Model, confidence/uncertainty, and the     │
│  learning loop (RFC-001) live HERE, once, and nowhere else.           │
└───────────────────────────────────────────────────────────────────────┘
```

### Layer 1 — Core Intelligence Layer (the one brain)

This is the existing pipeline, unchanged in responsibility: the Provider Layer,
Context Engine, Decision Engine, Language Engine, and the supporting services
(Memory, Decision Library, Knowledge Platform). **All reasoning lives here.** The
[Biological Model](../docs/biological-model.md) — Plant State, Stress, Disease Risk,
Growth Potential, Confidence, Uncertainty — is reasoned about exactly once, in this
layer. Business logic stays model-independent (ADR-003); reasoning stays separate
from language (ADR-001). Nothing above this layer re-implements any of it.

### Layer 2 — Specialist Agents Layer (consumers, not reasoners)

A **specialist agent is a bounded view onto the core**, defined entirely by
configuration, not by new intelligence. Concretely, an agent is the triple:

- **Scope** — the slice of reality it cares about (subjects, concerns, locations).
  *Climate Keeper* scopes to climate readings, VPD, and zone setpoints; *Plant
  Doctor* scopes to disease/pest signals and susceptibility.
- **Decision types** — which entries in the shared **Decision Library** it is
  responsible for surfacing (e.g. Climate Keeper → "climate-vs-target deviation").
- **Objective slice** — which part of the multi-objective **Biological Goals** it
  optimises for, so its recommendations name the goal they serve.

An agent therefore *calls the same Context Engine* (parameterised by its scope) and
*requests decisions from the same Decision Engine* (filtered to its decision types).
It receives structured Recommendations from the core, contributes Observations and
outcome feedback back into the core (feeding Memory / RFC-001), and **holds no
reasoning logic and no model dependency of its own.** Two agents looking at the same
plant see the *same* Plant State estimate with the *same* confidence — because there
is only one estimate, in the core.

The **AI COO** is a special agent: an **orchestrator**, not a reasoner. It does not
analyse raw data (consistent with the Agent Handbook's "never reads sensors
directly"). It composes the specialists' structured outputs into one operating
picture: prioritising, de-duplicating overlapping recommendations, and resolving
conflicts using the **decision hierarchy** from the Agent Handbook —
*plant health → people → product quality → production → energy → cost → speed.*
That single composed picture is what the User Interfaces Layer renders as Morning
Intelligence.

The **Learning Engine** is likewise an agent view, not a parallel brain: it is the
specialist embodiment of the learning loop proposed in
[RFC-001](RFC-001-feedback-and-learning-loop.md), reading Memory and feeding refined
understanding back into the core rather than learning in isolation.

### Layer 3 — User Interfaces Layer

How the composed intelligence reaches the grower. Morning Intelligence is the
default (ADR-004); conversational follow-up and Even G2 glasses are additional
surfaces. This layer only *renders* the structured output produced below it —
structured first, rendered second, no layer assuming a screen.

### The key property: shared reasoning, never duplicated

The whole point is that **intelligence is defined once and reused, not copied per
agent.** Adding a new concern (say, a "Substrate/Irrigation" specialist) means
adding a scope + decision types + an objective slice — a *configuration*, plus any
new decision type specified in the Decision Library — **not** a new reasoner, not a
new model integration, not a private copy of the Biological Model. The cost of a new
specialist is small and additive; the reasoning, the confidence/uncertainty
discipline, and the learning loop are inherited from the core for free.

## Benefits

- **Reconciles the two visions** into one coherent architecture: the pipeline is the
  brain; the agents are the roles it plays; the COO is the conductor.
- **No duplicated intelligence.** One Context Engine, one Decision Engine, one
  Biological Model, one confidence/uncertainty treatment — reused by every agent.
- **Consistency by construction.** Agents cannot disagree about a plant's state,
  because they share the estimate rather than each computing one.
- **Agents become an organising vocabulary** for concerns, ownership, and UI
  grouping — the legible "company of specialists" the product wants — without
  fragmenting the engine.
- **Cheap extensibility.** New specialists are configuration over the core, so the
  system scales in breadth without scaling in reasoning surface area.
- **Preserves the founding ADRs.** ADR-001 (reason vs. language), ADR-002
  (providers), and ADR-003 (model-independent core) all hold unchanged; this RFC
  sits on top of them.

## Risks

- **Conceptual surface area before any engine exists.** We are naming a structure we
  cannot yet exercise; the agent boundaries may prove wrong until real decisions
  exist. Mitigation: adopt as model only; build nothing now.
- **Drift toward fat agents.** The failure mode this RFC exists to prevent —
  an agent quietly accreting its own logic or its own LLM call — must be guarded by
  review. Rule of thumb: *if an agent reasons, the abstraction has leaked.*
- **Orchestrator as god-object.** The AI COO could grow into an unbounded
  coordinator. Its remit must stay narrow: prioritise, deduplicate, resolve by the
  stated hierarchy — not reason.
- **Conflict resolution is non-trivial.** The decision hierarchy is a clean
  tie-breaker on paper; real conflicts may need richer policy. Deferred until there
  are conflicting recommendations to study.
- **Over-design.** A dozen agents is a vision target, not a Sprint 1 need. Defining
  families we never populate would violate "ask, don't assume."

## Migration strategy

1. **Adopt this RFC as the model.** If accepted, record it as an ADR (e.g.
   **ADR-006 — Layered specialist-agent architecture**) and only then update
   [`docs/architecture.md`](../docs/architecture.md) to show the three layers and to
   add a short, normative definition of "agent" (scope + decision types + objective
   slice; no reasoning, no model).
2. **Promote the decision hierarchy** (plant health → … → speed) into a first-class
   place — either the architecture doc or the Biological Model — as the canonical
   conflict-resolution rule used by the AI COO.
3. **Implementation stays deferred.** Sprint 1 still builds *only* the single
   pipeline and one narrow decision (per the Sprint 1 backlog). The first
   "specialist agent" is then nothing more than a thin scope over that decision
   (e.g. **Climate Keeper = the climate-vs-target decision type from S1-08**),
   proving the pattern with zero new reasoning.
4. **No code rework later**, because the contract — "agents consume the core; the
   core owns reasoning" — is fixed now, before any agent or engine is written.

## Open questions

1. **Is an agent a runtime component or a configuration/namespace?** Could a
   specialist simply be a registered (scope + decision-type + objective) record the
   core executes, with no separate process?
2. **Where does orchestration live?** Is the AI COO a distinct service in the Agents
   Layer, or a composition policy inside the Context/Decision boundary? (Leaning
   toward a thin, explicit orchestrator so its narrow remit stays visible.)
3. **Do agents ever own a prompt?** Per ADR-001 only the Language Engine phrases.
   Does an agent get a per-concern *rendering* prompt (still in the core, still "one
   prompt = one feature"), or is all phrasing concern-agnostic?
4. **How do per-agent objective slices compose** back into the single
   multi-objective Biological Goals function without double-counting or conflict?
5. **Does the AI COO need its own memory** of cross-agent decisions, or does it read
   the same Memory the core writes?
6. **Granularity:** which specialists are real, separable concerns vs. convenient
   labels? The dozen in the Agent Handbook is a vision target, not a commitment.
