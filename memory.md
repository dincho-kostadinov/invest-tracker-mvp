# Memory — Feature 00: Monorepo + Skeletons

Last updated: 2026-09-17

## What was built

- `backend/`: FastAPI app (Python 3.12, `uv`-managed). Folder structure per
  `01-architecture.md` (`app/api`, `app/domain`, `app/marketdata`,
  `app/connectors`, `app/models`, `app/schemas`, `app/core`, `app/jobs`,
  `alembic/`, `tests/`). `GET /health` in `app/api/health.py` (runs
  `SELECT 1`, returns 503 + logs on DB failure). Config via
  `app/core/config.py` (pydantic-settings: `DATABASE_URL`,
  `FRONTEND_ORIGIN`). Ruff + mypy (strict) configured in `pyproject.toml`,
  both clean. One pytest (`tests/test_health.py`) passing against real
  Postgres. `Dockerfile` + `.dockerignore`.
- `frontend/`: Next.js App Router + TypeScript strict, npm. Minimal hand
  written typed client at `lib/api/client.ts` + `lib/api/health.ts` (no
  OpenAPI-generated client yet — deferred to feature 01). `app/page.tsx`
  server-fetches `/health` and renders status, with logged (not silent)
  error fallback. ESLint + `tsc --noEmit` both clean. `Dockerfile` +
  `.dockerignore`. `.nvmrc` pins Node 20.
- Root: `docker-compose.yml` — `db` (Postgres 16, daily-dev default via
  `docker compose up db`), `backend`, `frontend` (both with Dockerfiles, so
  `docker compose up` alone also runs the full stack — `frontend` gates on
  `backend`'s healthcheck, which gates on `db`'s). `.github/workflows/ci.yml`
  runs lint + type-check for both apps (not yet verified on an actual push).
  Root `.gitignore` added. `README.md` got a "Local Development" section.

## Decisions made

- Postgres always via Docker; daily-dev = DB in Docker + both apps run
  natively for hot reload. Full-Docker (`docker compose up`) is an
  alternative path, not the default loop — developer explicitly asked for
  both Dockerfiles to exist even though native is the daily driver.
- Python deps: `uv`. Node deps: `npm`.
- Lint/type-check tooling and a basic CI workflow were pulled into this
  scaffolding feature rather than deferred, so every later feature is
  checked from day one.
- Frontend API client is a hand-rolled minimal fetch wrapper for now; the
  OpenAPI-generated client (per `04-library-docs.md`) is deferred until
  there's more than one backend route.
- Health-check DB logic stays in the router (`app/api/health.py`), not
  `app/domain/` — moving it would violate the stronger "domain layer must
  stay framework-free / no SQLAlchemy imports" invariant in
  `01-architecture.md`. Documented with an inline comment.

## Problems solved

- `create-next-app`'s generated `frontend/.gitignore` has a blanket `.env*`
  rule that was also swallowing `.env.local.example` (which should be
  committed as a template). Fixed with a `!.env.local.example` negation.
- `NEXT_PUBLIC_*` env vars are inlined at Next.js **build** time, not just
  read at runtime — and since `getHealth()` runs server-side (Server
  Component) inside the frontend *container*, the Docker build arg for
  `NEXT_PUBLIC_API_URL` had to be Docker's internal service DNS name
  (`http://backend:8000`), not `localhost`. Wired via `ARG`/`ENV` in
  `frontend/Dockerfile` + `args:` in `docker-compose.yml`. Flagged in a
  comment as needing revisiting if a client-side (browser) call to the API
  is ever added.
- Docker Desktop wasn't running at first (`docker info` failed with a named
  pipe error) — `Start-Process` on Docker Desktop.exe, then poll
  `docker info` until ready, fixed it.
- `/review` (code-review skill) caught: frontend's health-check catch block
  was empty (violates code-standards' "no empty catch, log with
  `[module.function]` prefix") — fixed. `docker-compose.yml`'s `backend`
  service had no healthcheck, so `frontend`'s `depends_on` only waited for
  container start, not readiness — could flake on cold start — fixed by
  adding a `python -c urllib.request...` healthcheck to `backend` and
  switching `frontend` to `depends_on: backend: condition: service_healthy`.
  `03-code-standards.md`'s env var table was missing `FRONTEND_ORIGIN` —
  fixed.

## Active spec

`specs/00-monorepo-skeletons.md` — Status: **Built**. All "Done when" boxes
checked except "CI workflow runs both lint/type-check jobs on push and
passes" (workflow exists and mirrors the exact commands verified locally,
but no push/PR has actually triggered it yet).

## Current state

- Everything works and is verified: native hot-reload path (Postgres in
  Docker + `uv run uvicorn --reload` + `npm run dev`) and full
  `docker compose up --build` path both tested end-to-end — the frontend
  correctly shows live `status: ok / database: connected` from a real HTTP
  call to the backend in both modes.
- `context/08-progress-tracker.md` updated: Phase 0 marked done, Phase now
  reads "Phase 1 — Foundation", Next = "01 Auth + app shell".
- **Nothing has been committed.** `git status` shows README.md and
  context/08-progress-tracker.md modified, plus untracked: `.github/`,
  `.gitignore`, `backend/`, `docker-compose.yml`, `frontend/`,
  `specs/00-monorepo-skeletons.md`, `context/03-code-standards.md` (env var
  table fix). Local-only, gitignored: `backend/.env`, `frontend/.env.local`
  (both copied from their `.example` files during verification).
- Docker containers for the full-stack test were torn down
  (`docker compose down`) after verification — nothing left running.

## Next session starts with

Either:
1. Commit this feature (user hasn't asked for a commit yet — ask first), or
2. Run `/architect` for **"01 Auth + app shell"** (backend: JWT auth with
   Google OAuth + email/password, `/me`, protected-route dependency;
   frontend: login page, auth'd layout + nav, token in httpOnly cookie —
   see `context/02-build-plan.md` for the full Done-when).

## Open questions

- None from feature 00. CI has not actually been exercised by a real push —
  worth confirming it goes green the first time this branch/PR is pushed.
