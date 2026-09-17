# Spec — Monorepo + Skeletons

Status: Built
Created: 2026-09-17   ·   Last updated: 2026-09-17
Phase / Feature: Phase 0 · 00

> Written by /architect, confirmed by the developer before any code.
> /review checks the built feature against this file.

## What we are building

A monorepo skeleton with two independent apps: `backend/` (FastAPI, Python
3.12, `uv`-managed) exposing a single `GET /health` route that checks the DB
connection, and `frontend/` (Next.js App Router, TypeScript strict, npm)
with one page that calls that health endpoint through a minimal typed client
and renders the result. Postgres runs via Docker Compose. Both apps also get
their own `Dockerfile` and are wired into `docker-compose.yml` so the whole
stack can run with a single `docker compose up`, in addition to the native
hot-reload dev loop. Lint/type-check tooling (Ruff, mypy, ESLint, `tsc`) and
a CI workflow running them are included from the start.

## Language we agreed on

- **Skeleton**: the folder structure, tooling, and one trivial endpoint
  needed to prove both apps run and talk to each other and the DB — no
  business logic, auth, or data model yet.
- **Daily-dev default**: Postgres in Docker (`docker compose up db`), both
  apps run natively (`uv run uvicorn ...`, `npm run dev`) for fast reload.
- **Full-Docker path**: `docker compose up` with no arguments, building and
  running `db` + `backend` + `frontend` as containers — an alternative path
  for onboarding or a close-to-prod smoke test, not the default loop.

## Decisions made

- **Local Postgres via Docker Compose**: reproducible, no local install
  required.
- **Backend Dockerfile + frontend Dockerfile, both wired into
  `docker-compose.yml`**: so the entire stack can also run in Compose, not
  just the DB. (Developer-requested addition to the original scaffolding
  plan.)
- **Python deps via `uv`**: modern, fast, single lockfile.
- **Node deps via `npm`**: ships with Node, zero extra install.
- **Lint/format/type-check configs included now** (Ruff, mypy, ESLint,
  `tsc --noEmit`): `03-code-standards.md` mandates these; wiring them in from
  feature 00 means every subsequent feature is checked from day one.
- **Basic CI (GitHub Actions) added now**: runs lint + type-check for both
  apps on push/PR. No build/deploy step — hosting is a future ADR.
- **Frontend API client is a hand-rolled minimal fetch wrapper for this
  feature**, not the OpenAPI-generated client described in
  `04-library-docs.md` — generating a client for a single `/health` route
  isn't worth it; the generated client is wired in once there's a real API
  surface (feature 01).

## Assumptions

- Node LTS (20.x) and Python 3.12 are pinned (`.nvmrc` for Node,
  `requires-python` in `pyproject.toml` for Python).
- No auth, DB models, or business logic in this feature — those are
  features 01–02.
- No tests beyond what's trivially needed for the health check — no domain
  logic exists yet to unit test.
- CI does not build the Dockerfiles (no registry/deploy target exists until
  hosting is chosen in a future ADR) — it only runs lint/type-check.

## Scope

**In scope:**
- `backend/` FastAPI skeleton with the folder structure from
  `01-architecture.md` (`app/api`, `app/domain`, `app/marketdata`,
  `app/connectors`, `app/models`, `app/schemas`, `app/core`, `app/jobs`,
  `alembic/`, `tests/`); `GET /health` (DB-connected check); Ruff + mypy
  config; `backend/Dockerfile`
- `frontend/` Next.js skeleton (`app/`, `components/`, `lib/api/`); one page
  calling `/health` and rendering the result; ESLint + TS strict config;
  `frontend/Dockerfile`
- `docker-compose.yml`: `db` (Postgres 16, always used for daily dev),
  `backend`, `frontend` (both optional full-stack-in-Docker services)
- `.env.example` (backend) / `.env.local.example` (frontend)
- `.github/workflows/ci.yml`: lint + type-check for both apps
- README dev-setup section covering both the native and full-Docker
  workflows

**Out of scope:**
- Auth, DB models/migrations, business logic, real market data,
  deploy/hosting
- OpenAPI-generated typed client
- Any tests beyond the trivial health-check test

## How to build it

1. `backend/`: `pyproject.toml` (fastapi, uvicorn, sqlalchemy,
   pydantic-settings + ruff, mypy, pytest as dev deps); `app/core/config.py`
   (Settings via pydantic-settings, `DATABASE_URL`); `app/core/db.py`
   (SQLAlchemy engine + session dependency); `app/api/health.py`
   (`GET /health` runs `SELECT 1`); `app/main.py` (FastAPI app, health
   router, CORS for frontend origin); empty `app/domain/`,
   `app/marketdata/`, `app/connectors/`, `app/models/`, `app/schemas/`,
   `app/jobs/` (placeholder `__init__.py`); `alembic/` initialized (no
   migrations yet); `tests/test_health.py`; Ruff + mypy config in
   `pyproject.toml`; `.env.example`; `backend/Dockerfile`.
2. `frontend/`: Next.js App Router + TS strict + ESLint scaffold;
   `lib/api/client.ts` (minimal typed fetch wrapper reading
   `NEXT_PUBLIC_API_URL`) + `lib/api/health.ts` (`getHealth()`);
   `app/page.tsx` calls `getHealth()` and renders status; empty
   `components/`; `.env.local.example`; `frontend/Dockerfile`.
3. Root `docker-compose.yml`: `db`, `backend` (depends on `db`), `frontend`
   (depends on `backend`).
4. `.github/workflows/ci.yml`: `backend` job (uv sync, ruff check, mypy),
   `frontend` job (npm ci, eslint, tsc --noEmit).
5. Update root `README.md` with both dev workflows.
6. Update `context/08-progress-tracker.md`: mark this feature done, advance
   Next to "01 Auth + app shell".
7. Verify end-to-end per "Done when" below.

## Done when

- [x] `docker compose up db` starts Postgres locally.
- [x] `backend/`: `uv run uvicorn app.main:app --reload` starts the API;
      `GET /health` returns 200 with a DB-connected check.
- [x] `frontend/`: `npm run dev` starts Next.js; the home page renders and
      shows the backend health status fetched live.
- [x] `docker compose up` (no args) builds and starts `db` + `backend` +
      `frontend`, and the frontend container's health page reflects a live
      call to the backend container.
- [x] `ruff check` and `mypy` pass on `backend/`.
- [x] `eslint` and `tsc --noEmit` pass on `frontend/`.
- [ ] CI workflow runs both lint/type-check jobs on push and passes. (Not yet
      verified — no push/PR has run it; workflow mirrors the exact commands
      that passed locally.)

## Open questions

- None.
