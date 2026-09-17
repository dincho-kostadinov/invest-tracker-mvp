# AGENTS.md

This is a **reusable project skeleton** for building applications in a
predictable, context- and spec-driven way with the help of agents and skills.

It is stack-neutral. Everything in `context/` is a **template** — fill each
file in for the current project before building. Nothing here assumes a
specific framework, backend, or design system.

---

## Read Before Anything Else

Read these in order before any implementation. They are the source of truth
for this project — never assume, always verify against them.

1. `context/00-project-overview.md` — what is being built and why
2. `context/01-architecture.md` — stack, boundaries, data model
3. `context/02-build-plan.md` — phased feature roadmap
4. `context/03-code-standards.md` — engineering conventions
5. `context/04-library-docs.md` — project rules for third-party libraries
6. `context/08-progress-tracker.md` — current status, decisions, notes

**UI / frontend projects only** — also read the optional design module:

7. `context/05-ui-tokens.md` — design tokens (colors, type, spacing)
8. `context/06-ui-rules.md` — UI patterns and constraints
9. `context/07-ui-registry.md` — living registry of built components

If a spec exists for the feature you are about to build, read it too:
`specs/<feature>.md`. Architectural decisions are recorded in `adr/` — read the
relevant ADR before touching the area it governs.

---

## The Engineering Loop

```
/architect  →  writes specs/<feature>.md  →  Build  →  /review  →  Ship
                                               │
              /imprint   after every UI component (UI projects)
              /remember  save at end of session, restore at start
              /recover   when something breaks
   architectural decision along the way → write an ADR (adr/) + update context/
```

Predictable development depends on running the loop every time, not
occasionally. A skill used sometimes is a skill that cannot be relied on.

---

## Rules That Never Change

These are universal — they hold on every project built from this skeleton:

- **Spec before build** — for any non-trivial feature, run `/architect` and
  confirm the written spec in `specs/` before writing code.
- **Read context first** — never build against assumptions; verify against
  the `context/` files above.
- **Scope is sacred** — build only what the current feature requires. Do not
  add unrequested work, even if it seems helpful.
- **Respect architecture boundaries** — whatever boundaries
  `01-architecture.md` defines, never cross them.
- **Architectural decisions get an ADR** — adding, swapping, or removing a
  library, or changing a framework, boundary, invariant, or data model, is
  recorded as an ADR in `adr/` and then reflected in the `context/` files. An
  ADR is immutable once accepted; supersede it with a new one. Feature-level
  decisions stay in the spec, not in an ADR.
- **Every feature must be testable** — if it cannot be verified immediately
  after implementation, it is not done.
- **Update the trackers after every feature** — `08-progress-tracker.md`
  always, and `07-ui-registry.md` after any UI component.
- **Before any third-party library** — load its installed skill first, then
  read `04-library-docs.md` for project-specific rules.
- **One failed correction, then stop** — if the same problem persists after
  one corrective prompt, stop immediately and run `/recover`.

---

## Project-Specific Rules

Rules that depend on the chosen stack live in the context files, not here.
Fill these in per project:

- Design-system rules (e.g. token usage, no hardcoded values) →
  `05-ui-tokens.md` / `06-ui-rules.md` (UI projects only)
- Language, naming, and error-handling conventions → `03-code-standards.md`
- Library-specific patterns → `04-library-docs.md`

---

## Available Skills

Installed under `.claude/skills/`:

- `/architect` — before any non-trivial feature. Think it through, then write
  the spec to `specs/` — or, for an architectural decision, an ADR to `adr/`.
- `/review` — after building a feature. Verify it is correct, not just working.
- `/recover` — when something breaks after one failed correction.
- `/imprint` — after any new UI component. Capture patterns to the registry.
- `/remember save` — at the end of a session.
- `/remember restore` — at the start of a session.
