# Changelog

All notable changes to this project skeleton are documented here.
Format based on Keep a Changelog; versioning follows Semantic Versioning.

## [1.0.0] — 2026-09-04

First stable version — ready to test on a real project.

### Added
- **Context engineering** — `AGENTS.md` (+ `CLAUDE.md` importing it) and the
  numbered `context/` templates: overview, architecture, build-plan,
  code-standards, library-docs, progress-tracker, plus an optional UI module
  (ui-tokens, ui-rules, ui-registry, `designs/`).
- **Spec-driven development** — `specs/` with a per-feature `_TEMPLATE.md`;
  `/architect` writes the spec, `/review` verifies the build against it.
- **Architecture Decision Records** — `adr/` with `_TEMPLATE.md`; architectural
  decisions are recorded and then propagated into the `context/` files.
- **Skills** (`.claude/skills/`) — architect, review, imprint, recover, remember.
- **README** with the full "ticket → shipped feature" walkthrough and
  `how-it-works.png` diagram (including the ADR side branch).

### Principles baked in
- Stack-neutral — all project-specific content is placeholder, filled per project.
- Three record types kept distinct: `specs/` = per-feature intent ·
  `adr/` = architectural history (the *why*) · `context/` = current truth (the *what*).
- You provide the *what*; the pipeline produces the *how*; you approve each gate.

### Next
- Test on a real project; revise based on real friction (spec detail level,
  loop self-triggering, state overlap between specs/tracker/memory).
