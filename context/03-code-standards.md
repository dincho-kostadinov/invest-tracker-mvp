# Code Standards

Conventions the agent follows in every session. Stack is split per ADR-0002:
Python/FastAPI backend + Next.js frontend.

## Engineering Mindset (universal)

- Think before implementing; read context first; never assume.
- Scope is sacred — build only what the current feature requires.
- Every feature must be testable — if it can't be verified immediately, it's incomplete.
- Clean over clever. One thing at a time. Wrap risky/external calls in try/except (Py) or try/catch (TS) and log.

## Money & Numbers (both sides)

- Money is **integer minor units + currency code**. Never `float`/`number` for money.
- FX and unit conversions happen in the backend `domain` layer, never in UI or routers.

## Backend — Python / FastAPI

- Python 3.12, **full type hints** everywhere; enforce with **mypy**. Lint/format with **Ruff**.
- Routers are **thin**: parse (Pydantic) → call `domain` → return schema. No business logic in routers.
- Pydantic schemas for every request/response and every external payload.
- DB session via FastAPI dependency injection; never a global session.
- Prefer `async` for IO (HTTP, DB where supported). Never block the event loop.
- Domain layer is framework-free (no FastAPI/SQLAlchemy imports leaking business rules).
- Config via `pydantic-settings` from env; no hardcoded secrets/URLs.

## Frontend — Next.js / TypeScript

- `strict` on; no `any` (use `unknown` + narrow); explicit exported types.
- App Router; Server Components by default; `"use client"` only when needed.
- All backend access goes through the typed client in `frontend/lib/api` — no `fetch` scattered in components.
- Validate user input with Zod before sending.

## File & Folder Naming

- Python: modules `snake_case.py`, classes `PascalCase`. TS: components `PascalCase.tsx`, utils `camelCase.ts`. Folders `kebab-case`. One unit per file.

## Error Handling

- No empty except/catch. Log with a `[module.function]` prefix.
- User-facing errors are human-readable; never expose raw errors or provider internals.
- API errors return proper status + a generic message; details logged, not leaked.
- Market-data/connector failures are caught and degrade gracefully (stale price or manual fallback) — never crash a request or the job.

## Testing (required)

- **pytest** for backend `domain` — valuation, returns, FX, cost-basis (pure, must be covered). pytest for API routes (happy path + auth).
- **Vitest** for frontend units; **Playwright** for one e2e per phase (auth, add holding, dashboard).
- Write tests from the spec's **"Done when" (EARS)** criteria — each maps to ≥1 test. A feature is done when its criteria tests pass.

## Environment Variables

All config in env files (`.env` backend, `.env.local` frontend); never hardcode. Keep current:

| Variable | Used in |
| -------- | ------- |
| `DATABASE_URL` | backend/core/db |
| `JWT_SECRET`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` | backend/core/security |
| `MARKETDATA_*` (ADR-0001) | backend/marketdata |
| `NEXT_PUBLIC_API_URL` | frontend/lib/api |

## Dependencies

Before adding: does an existing dep / the framework already do it? A significant
dependency needs an **ADR** + a `04-library-docs.md` section. Approved so far:

- **Backend:** `fastapi`, `uvicorn`, `sqlalchemy`, `alembic`, `pydantic`, `pydantic-settings`, `authlib`/`python-jose`, `passlib`, `httpx`, `apscheduler`, `pytest`
- **Frontend:** `next`, `react`, `typescript`, `zod`, `recharts`, `vitest`, `@playwright/test`
