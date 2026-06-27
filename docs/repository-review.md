# Sprint 0 — Repository Review

Task 1 deliverable: an evaluation of the repository structure and the structural
changes recommended, **with the reasoning for each**. Per project rules,
architecture and structure evolve deliberately — so this review states *why*
before anything is treated as settled.

## Important caveat on "existing repository"

I do **not currently have read access to the live GitHub repository** (no GitHub
connector is connected to this workspace, and no repository contents were
provided). I therefore cannot audit the actual committed tree. This review
evaluates the **Sprint 0 structure established here** — the baseline intended to be
committed as the repository's foundation — and flags where the real repo, if it
already contains files, may differ.

> To make future reviews concrete, please either connect a GitHub connector or
> paste the current `git ls-files` / tree output. I will then reconcile this
> baseline against what actually exists.

## Structure under review

```
ptp-os/
├── README.md
├── docs/        vision, architecture, project-rules, roadmap, glossary, this review
├── specs/       greenhouse-provider (more added per feature)
├── domain/      19 entities (v1)
├── adr/         ADR-001…004
├── rfc/         RFC-001…002  ← added (see rationale below)
├── prompts/     conventions only (no prompts yet)
├── integrations/ provider catalog (no code yet)
└── services/    engine catalog (no code yet)
```

## Assessment

The requested seven-folder layout (`docs`, `specs`, `domain`, `adr`,
`integrations`, `prompts`, `services`) is sound for a long-lived,
documentation-first project. It cleanly separates *what/why* (docs, adr) from
*how* (specs) from *the model* (domain) from *the edges and the core*
(integrations, services). I recommend keeping it as-is, with the additions and
conventions below.

## Recommended structural changes (with rationale)

1. **Add an `rfc/` folder.** — *Why:* Task 6 requires that architectural change be
   proposed via RFC before adoption. ADRs record *accepted* decisions; RFCs hold
   *proposals under discussion*. Mixing the two in `adr/` would blur "decided" vs.
   "proposed" and undermine the deliberate-evolution rule. A dedicated `rfc/`
   keeps that boundary clean. Lifecycle: RFC → accepted → ADR → update
   `architecture.md`.

2. **Every folder has a `README.md` defining its purpose and conventions.** —
   *Why:* a new engineer should understand any folder without external context,
   and it prevents drift (people putting the wrong things in the wrong place).

3. **One file per domain entity (not a single `domain-model.md`).** — *Why:* the
   model has 19 entities and will grow; per-file keeps diffs small, ownership
   clear, and review focused. An index in `domain/README.md` preserves the
   overview.

4. **One file per ADR/RFC, sequentially numbered with a slug.** — *Why:*
   immutability and stable links. `ADR-002-provider-abstraction.md` is
   self-describing and never renumbered.

5. **Specs carry a status header and live one-per-component.** — *Why:* enforces
   "specification before implementation" and makes it obvious what is Draft vs.
   Agreed before code is written.

6. **Keep the Sprint 1 backlog as a doc now (`docs/sprint-1-backlog.md`), to
   become GitHub Issues.** — *Why:* I cannot create real GitHub Issues without a
   connector. The backlog is authored in-repo so it is reviewable; it can be
   pushed to Issues verbatim once GitHub is connected (see that file).

## Recommended additions for Sprint 1 (not created in Sprint 0)

These are noted, not built, to respect "no implementation in Sprint 0":

- **`/` tooling files** when code begins: `LICENSE`, `CONTRIBUTING.md`,
  `CODEOWNERS`, `.editorconfig`, `.gitignore`, and a `CHANGELOG.md`. *Why:* a real
  software product needs contribution norms and history from the first commit.
- **`tests/` (or co-located tests) including provider conformance tests.** *Why:*
  substitutability of providers must be *proven*, not assumed
  (see the provider spec, Section 6).
- **A top-level `/src` or service-per-folder code layout** — to be decided with the
  stack choice in Sprint 1 (a small RFC if non-obvious).

## Things deliberately *not* changed

- I did not rename or restructure the seven requested folders. They work.
- I did not add a product/UI folder — Sprint 0 builds no UI, and product design is
  out of my mandate.
- I did not pick an implementation language/framework. That is a Sprint 1 decision
  and, if non-trivial, deserves its own ADR/RFC rather than a silent default.

## Open questions for review
1. Does the live repo already contain files I should reconcile against?
2. ~~Is `rfc/` acceptable as a permanent part of the structure?~~ **Resolved
   (Sprint 0 review): yes — `rfc/` is a permanent part of the repository.**
3. Should the Sprint 1 backlog become GitHub Issues now (needs a connector) or
   stay as an in-repo doc for this review cycle?
