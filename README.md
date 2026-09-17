# Project Skeleton — Context- & Spec-Driven Development

**Version 1.0.0** · 2026-09-04 · [CHANGELOG](CHANGELOG.md)

A **reusable, stack-neutral skeleton** for building applications in a
predictable way with agents and skills. Copy this folder to start a new
project, fill in the `context/` templates for that project, and develop through
a fixed loop that keeps an AI agent aligned, consistent, and correct across
sessions.

Nothing here is tied to a framework, backend, or design system. The structure
is the reusable part; the content is filled in per project.

---

## Local Development — Invest Tracker

Stack: Next.js (`frontend/`) + FastAPI (`backend/`), Postgres via Docker.
Prereqs: Docker, Node 20 (`frontend/.nvmrc`), Python 3.12 with
[`uv`](https://docs.astral.sh/uv/).

### Native (day-to-day, hot reload)

```
docker compose up db                         # Postgres only

cd backend
cp .env.example .env
uv sync
uv run uvicorn app.main:app --reload         # http://localhost:8000/health

cd frontend
cp .env.local.example .env.local
npm install
npm run dev                                  # http://localhost:3000
```

### Full stack in Docker

```
docker compose up --build                    # db + backend + frontend
```

Frontend at `http://localhost:3000`, backend at `http://localhost:8000`.

### Checks

```
cd backend && uv run ruff check . && uv run mypy .
cd frontend && npm run lint && npm run typecheck
```

---

## How It Fits Together

- **`AGENTS.md`** — the agent's operating manual. Read first every session.
  `CLAUDE.md` just imports it, so there is one source of truth.
- **`context/`** — the project's source of truth, as templates to fill in:
  overview, architecture, build plan, code standards, library docs, progress
  tracker, and an **optional UI module** (tokens, rules, registry) for
  frontend projects.
- **`specs/`** — one durable spec per feature. Written before building,
  verified against after; this is what makes the process *spec-driven*. One
  file per feature (`specs/<feature>.md`, kebab-case) — copy
  `specs/_TEMPLATE.md` to start, update it if decisions change during the
  build, and keep it as the record after shipping.
- **`adr/`** — architecture decision records. One immutable file per
  *architectural* decision (add/swap/remove a library, change a framework,
  boundary, invariant, or data model). Copy `adr/_TEMPLATE.md` to
  `adr/<NNNN>-<title>.md`. The three record types stay distinct: **`specs/` =
  per-feature intent · `adr/` = architectural history (the *why*) · `context/`
  = current truth (the *what*).**
- **`context/designs/`** — (UI projects) drop design exports here — screenshots,
  mockups, Figma frames; `06-ui-rules.md` treats them as the visual source of
  truth. Leave empty for non-UI projects.
- **`.claude/skills/`** — the five workflow skills below.

---

## Using the Skeleton on a New Project

1. Copy this folder.
2. Fill in `context/00`–`04` and `08`. For a UI project, also fill `05`–`07`;
   otherwise leave the UI module empty.
3. Make the invariants in `01-architecture.md` concrete for the chosen stack.
4. Start building through the loop below.

Every `context/` file marks what to fill with `<!-- FILL -->` placeholders.

---

## How It Works — From Ticket to Shipped Feature

You provide the **"what"**, the pipeline produces the **"how"**, and you approve
it at each gate. Nothing is built from a vague prompt, and nothing built is lost
between sessions.

**You write the ticket. The agent writes the spec, tasks, and acceptance
criteria — you review and confirm.**

Where work lives: your **Jira epics/stories** are the *map* in
`context/02-build-plan.md` (one line per feature; or Jira *is* your map).
`/architect` expands one map line — or one pasted ticket — into the *detail* in
`specs/<feature>.md`.

### The cycle — four gates, you approve each

**1. Ticket → Spec** *(thinking gate)* — bring a story or the next map line:

```
/architect Here's the story: [paste Jira title + description + acceptance criteria]. Write the spec.
```

It aligns on decisions, writes `specs/<feature>.md`, waits for `Confirmed.`
*Epic → Phase · Story → feature · story's acceptance criteria → spec's "Done when" · agent's breakdown → spec's build steps.*

**2. Spec → Build** *(implementation gate)*:

```
Build this feature following specs/<feature>.md. Stay in scope.
```

*(UI: run `/imprint` after each component.)*

**3. Build → Review** *(correctness gate)*:

```
/review <feature>
```

Checks spec match, architecture/standards, and production-readiness. You decide fixes.

**4. Review → Ship** *(record gate)*:

```
Update context/08-progress-tracker.md — mark the feature done, note decisions.
```

Commit. The spec stays as the record. Loop back for the next ticket.

**Across sessions:** `/remember restore` at the start, `/remember save` at the
end. Stuck after one failed fix → `/recover`.

### Worked example — one task, end to end

Task from Jira: **"Shorten a URL — paste a long URL, get a short code."**

```
1.  /remember restore
    -> rebuilds context. (Skip on the very first session.)

2.  /architect Story: "Shorten a URL — user pastes a long URL and gets a
    short code back." Acceptance: valid URL -> unique code; invalid -> error.
    Write the spec.
    -> asks: code length? reuse code for duplicates? You answer.
    -> writes specs/shorten-url.md. You reply: Confirmed.

3.  Build this feature following specs/shorten-url.md. Stay in scope.
    -> creates the migration, POST /shorten, and the form page.

4.  /imprint          (UI project — captures the form's pattern)

5.  /review shorten-url
    -> "Layer 2: input not validated before insert (Important)." You reply:
       Fix the Important issue.

6.  Update context/08-progress-tracker.md — mark 01 done.
    -> then commit.

7.  /remember save    (end of session)
```

That is the full loop for one ticket. The next feature repeats from step 2.

---

## Changing the Architecture or Adding a Library

Feature decisions live in the spec. **Architectural** decisions — adding,
swapping, or removing a library, or changing a framework, boundary, invariant,
or data model — go through `/architect` and are recorded as an **ADR** in
`adr/`, then reflected in the `context/` files (architecture, approved
dependencies, library docs). The ADR is the immutable *why*; the context files
are the current *what*. Write an ADR only when the decision is hard to reverse
or crosses more than one feature — a trivial local choice just goes in the spec.

---

## Skills

### `/architect` — before building anything
Think through the feature like a senior engineer, align on language and the
decisions that matter, then **write the spec** to `specs/<feature>.md` and
confirm it before any code. A thinking session, not a grilling session.

### `/review` — after building any feature
Verify the build is *correct*, not just working. Three layers: does it match
the spec, does it respect the architecture and standards, is it production
ready. Reports issues; the developer decides what to fix.

### `/recover` — when something breaks
Diagnose the failure type before responding: targeted fix (isolated bug), hard
reset (polluted session), or rethink (wrong foundation). The right response
depends on the right diagnosis.

### `/remember` — at session boundaries
AI has no memory between sessions. `save` compresses what matters into
`memory.md`; `restore` rebuilds context at the start of the next session and
confirms before continuing.

### `/imprint` — after any UI component (UI projects)
Extract the visual patterns that matter and append them to
`context/07-ui-registry.md`, so every later component matches. `audit` mode
scans an existing codebase and establishes a baseline.

---

## Principles

- **Read context first** — never build against assumptions.
- **Spec before build** — the agreed intent lives in a file, not the chat.
- **Scope is sacred** — build only what the feature requires.
- **Testable or unfinished** — if it can't be verified now, it isn't done.
- **One failed correction, then stop** — run `/recover` instead of patching blind.
