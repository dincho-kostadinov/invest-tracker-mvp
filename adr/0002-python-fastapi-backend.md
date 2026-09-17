# ADR-0002 — Split architecture: Next.js frontend + Python/FastAPI backend

Status: Accepted
Date: 2026-09-17
Deciders: Dincho
Related: context/01-architecture.md, context/03-code-standards.md, context/04-library-docs.md, ADR-0001

## Context

The initial architecture assumed an all-in-one Next.js app with Prisma. The
owner wants the backend in **Python + FastAPI** (business logic, valuation jobs,
and market-data integration are a better fit for Python, and it matches the
preferred stack).

## Decision

Split into two apps in one monorepo:

- **`frontend/`** — Next.js (App Router, TS strict), **UI only**. Talks to the
  backend over REST via a typed API client. No DB or market-data access.
- **`backend/`** — Python 3.12 + FastAPI. Owns API, business logic, data, and
  the scheduled valuation job.

Supporting choices:
- **Data:** PostgreSQL via **SQLAlchemy** + **Alembic** migrations (replaces Prisma).
- **Validation/schemas:** **Pydantic** (backend), Zod (frontend inputs).
- **Auth:** owned by the backend — **JWT** with **Google OAuth + email/password**;
  frontend stores the token in an httpOnly cookie and sends it on requests.
- **Contract:** FastAPI OpenAPI schema → generated/typed client on the frontend.
- **Scheduling:** APScheduler (or a cron-invoked script) inside the backend.

This supersedes the all-Next.js/Prisma stack in the original `01-architecture.md`.

## Alternatives considered

- **All-in-one Next.js + Prisma** — rejected: owner wants a Python backend.
- **Next.js API routes calling a small Python microservice** — rejected: keeps
  two runtimes without a clean full backend; more glue than a clean split.

## Consequences

- Two runtimes and an API boundary → an API contract to keep in sync (mitigated
  by generating a typed client from FastAPI's OpenAPI schema).
- Python tooling added: `uv`/`poetry`, Ruff, mypy, pytest.
- Clear separation of concerns and independent scaling; matches the preferred stack.
- Auth now lives backend-side; the frontend is a pure client.

## Follow-up — reflect this decision in the living context

- [x] `context/01-architecture.md` — split stack, folders, boundaries, data flow, auth
- [x] `context/03-code-standards.md` — Python conventions + pytest
- [x] `context/04-library-docs.md` — FastAPI, SQLAlchemy/Alembic, Pydantic, auth, httpx
- [x] `context/02-build-plan.md` — features 01/02/05 adjusted for the split
- [ ] Hosting target — future ADR
