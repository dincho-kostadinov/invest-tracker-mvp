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

## Data Model (first cut)

| Table | Key fields |
| ----- | ---------- |
| `users` | id, email, password_hash?, oauth fields |
| `accounts` | id, user_id, name, type (`fund_platform`\|`broker`\|`physical`) |
| `assets` | id, kind (`FUND`\|`GOLD`\|`STOCK`), name, isin?, symbol?, currency, unit (`share`\|`gram`) |
| `holdings` | id, user_id, account_id, asset_id, quantity, avg_cost_minor, currency |
| `transactions` | id, user_id, holding_id, type (`BUY`\|`SELL`\|`DIVIDEND`\|`FEE`), quantity, price_minor, currency, fee_minor, occurred_at |
| `price_snapshots` | id, asset_id, as_of, price_minor, currency, source |
| `fx_rates` | id, as_of, base, quote, rate |
| `portfolio_snapshots` | id, user_id, as_of, total_value_minor, base_currency (EUR) |

## Returns

Period return = current total value vs the `portfolio_snapshots` row at the start
of the period (day/week/month/year). The daily job writes today's snapshot;
current value is computed from the latest `price_snapshots` + `fx_rates`.

## Authentication

- Backend-owned: JWT; Google OAuth + email/password. Token in an httpOnly cookie.
- Every endpoint resolves the `user_id` from the token; frontend never trusts client-side identity.
- Protected API routes require a valid token; every query is scoped to that user.

## Invariants

- The **frontend never calls the DB or market data directly** — only the backend API.
- Money is stored as **integer minor units + a currency code** — never a float.
- All market-data/platform calls go through the backend `marketdata` / `connectors`
  interfaces, wrapped in try/except, cached, never from routers or the frontend.
- Every query is scoped to the current user — no cross-user access, ever.
- Secrets/API keys are backend-only.
- Any change to the stack, a boundary, an invariant, the data model, or a
  market-data/library choice is recorded as an ADR in `adr/` and reflected here.
