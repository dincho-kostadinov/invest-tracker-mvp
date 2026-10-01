# Architecture

> Stack decided in ADR-0002 (Next.js frontend + Python/FastAPI backend).

## Stack

| Layer | Tool | Purpose |
| ----- | ---- | ------- |
| Frontend | Next.js (App Router), TypeScript strict | UI only; calls the backend API |
| Backend | Python 3.12 + FastAPI | API, business logic, jobs |
| Database | PostgreSQL + SQLAlchemy + Alembic | data + migrations |
| Auth | Backend-owned: JWT + Google OAuth + email/password | sessions, per-user isolation |
| Validation | Pydantic (backend), Zod (frontend inputs) | boundary validation |
| Market data | Python provider behind an interface — see ADR-0001 | fund NAV, gold spot, FX |
| Scheduling | APScheduler / cron-invoked script (backend) | daily price + portfolio snapshots |
| API contract | FastAPI OpenAPI → typed client on the frontend | keep FE/BE in sync |
| Charts | Recharts (frontend) | dashboard |
| Hosting | TBD — future ADR | — |

## Folder Structure (monorepo)

```
/
├── AGENTS.md · CLAUDE.md · context/ · specs/ · adr/
├── frontend/                 # Next.js — UI only
│   ├── app/                  # pages; calls the backend via lib/api
│   ├── components/           # UI only
│   └── lib/api/              # typed backend client (from OpenAPI)
└── backend/                  # FastAPI
    ├── app/
    │   ├── api/              # routers — thin, no business logic
    │   ├── domain/           # portfolio, valuation, returns — business logic
    │   ├── marketdata/       # provider interface + implementations
    │   ├── connectors/       # platform position-sync (best-effort)
    │   ├── models/           # SQLAlchemy models
    │   ├── schemas/          # Pydantic request/response
    │   ├── core/             # config, security (JWT), db session
    │   └── jobs/             # scheduled valuation job
    ├── alembic/              # migrations
    └── tests/
```

## System Boundaries

| Area | Owns | Must NOT do |
| ---- | ---- | ----------- |
| `frontend/app` | pages + calls to `lib/api` | business logic; DB or market-data calls |
| `frontend/components` | UI rendering | data fetching logic |
| `backend/app/api` | HTTP routers, thin | business logic |
| `backend/app/domain` | valuation, returns, portfolio rules | HTTP/DB framework details, external HTTP |
| `backend/app/marketdata`, `connectors` | all external calls, behind interfaces | leak vendor details upward |
| `backend/app/models` + `alembic` | schema + data access | — |

## Data Flow

- **Reads:** frontend → `lib/api` → FastAPI router → `domain` → DB → response.
- **Mutations:** frontend action → API → `domain` → DB → response; frontend revalidates.
- **Valuation (scheduled):** backend job → `marketdata` (NAV + gold spot + FX) → write `price_snapshots` + `fx_rates` → compute + write `portfolio_snapshots`.

## Data Model

> Built in feature 02 (`specs/02-database-schema.md`). Numeric types per ADR-0003,
> per-user assets + DB-enforced ownership per ADR-0004. All PKs are UUID.

| Table | Key fields |
| ----- | ---------- |
| `users` | id, email, password_hash?, google_id?, name? |
| `accounts` | id, user_id, name, type (`fund_platform`\|`broker`\|`physical`) |
| `assets` | id, **user_id**, kind (`FUND`\|`GOLD`\|`STOCK`), name, isin?, symbol?, currency, unit (`share`\|`gram`) — unique (user_id, isin) |
| `holdings` | id, user_id, account_id, asset_id, quantity `NUMERIC(20,8)`, **cost_basis_minor**, currency — unique (account_id, asset_id) |
| `transactions` | id, user_id, holding_id, type (`BUY`\|`SELL`\|`DIVIDEND`\|`FEE`), quantity?, price `NUMERIC(20,6)`?, amount_minor, fee_minor, currency, occurred_at |
| `price_snapshots` | id, asset_id, as_of `DATE`, price `NUMERIC(20,6)`, currency, source — unique (asset_id, as_of) |
| `fx_rates` | id, as_of `DATE`, base, quote, rate `NUMERIC(20,8)` — unique (as_of, base, quote); global |
| `portfolio_snapshots` | id, user_id, as_of `DATE`, total_value_minor, base_currency (EUR) — unique (user_id, as_of) |

- **Ownership:** `holdings` → `accounts`/`assets` and `transactions` → `holdings` use
  composite FKs on `(parent_id, user_id)`, so a cross-user link is rejected by the DB.
- **Deletes:** user → cascades everything; account/asset still used by a holding →
  restricted; asset → cascades its price_snapshots; holding → cascades its
  transactions; portfolio_snapshots are never touched by holding/asset deletes.
- **Enumerations** are `VARCHAR` + `CHECK` constraints backed by Python `StrEnum`s
  (not native Postgres `ENUM`).

## Returns

Period return = current total value vs the `portfolio_snapshots` row at the start
of the period (day/week/month/year). The daily job writes today's snapshot;
current value is computed from the latest `price_snapshots` + `fx_rates`.

## Authentication

- Backend-owned: JWT (Authlib); Google OAuth + email/password. Every endpoint resolves
  the `user_id` from the token via `Depends(get_current_user)`; frontend never trusts
  client-side identity. Protected API routes require a valid token; every query is
  scoped to that user.
- **The httpOnly session cookie is set by the frontend, not the backend** — frontend
  and backend are different origins, so a cookie set directly by the backend would be
  invisible to Next.js `proxy.ts` and to Server Components reading via `next/headers`.
  Backend `/auth/*` endpoints are plain JSON (`{access_token}`), never `Set-Cookie`.
  Next.js Route Handlers (`frontend/app/api/auth/*`) receive that token and set the
  cookie on the frontend's own domain; every authenticated request then reads it via
  `next/headers` and forwards it as `Authorization: Bearer <token>`. The backend still
  owns 100% of the auth logic (issuing, signing, validating JWTs, the Google OAuth
  exchange) — only which HTTP layer writes the cookie differs from a same-origin setup.
  Full mechanism, including the Google OAuth same-origin-then-one-time-code handoff:
  `specs/01-auth-app-shell.md`.

## Invariants

- The **frontend never calls the DB or market data directly** — only the backend API.
- Money **amounts** are stored as **integer minor units + a currency code**; unit
  prices, quantities, and FX rates as exact `NUMERIC` (`Decimal`) — never a float
  (ADR-0003). Holdings store total cost basis, not a per-unit average.
- Per-user ownership is **enforced by the database** via composite FKs (ADR-0004).
- All market-data/platform calls go through the backend `marketdata` / `connectors`
  interfaces, wrapped in try/except, cached, never from routers or the frontend.
- Every query is scoped to the current user — no cross-user access, ever.
- Secrets/API keys are backend-only.
- Any change to the stack, a boundary, an invariant, the data model, or a
  market-data/library choice is recorded as an ADR in `adr/` and reflected here.
