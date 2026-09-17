# Build Plan

> Stack is split per ADR-0002. Most features touch **both** `backend/` (FastAPI)
> and `frontend/` (Next.js). Build the backend endpoint + tests first, then the
> UI against it.

## Core Principle

Small, visible, testable increments. UI pages built against real (or stubbed)
API responses. Every feature shippable and testable before the next.

## Phase 0 — Scaffolding

### 00 Monorepo + skeletons
- **Build:** `frontend/` (Next.js) + `backend/` (FastAPI) in one repo; Postgres connection; health-check endpoint; frontend calls it.
- **Done when:** both apps run locally, frontend shows backend health OK, DB connects.

## Phase 1 — Foundation

### 01 Auth + app shell
- **Backend:** JWT auth (Google OAuth + email/password), `/me`, protected-route dependency.
- **Frontend:** login page, auth’d layout + nav, token in httpOnly cookie.
- **Done when:** a user can sign up, log in, hit a protected page, and be redirected when unauthenticated.

### 02 Database schema
- **Backend:** SQLAlchemy models for all tables in `01-architecture.md` + Alembic migration; seed script with the owner’s sample holdings.
- **Done when:** migrations run clean and seed inserts a user with Amundi/Schroders funds + gold.

### 03 Dashboard UI (mock data)
- **Frontend:** dashboard with total value, period-return tiles (D/W/M/Y), allocation chart, holdings summary — mock data.
- **Done when:** dashboard renders correctly and is responsive.

## Phase 2 — Holdings & Valuation

### 04 Holdings CRUD + Settings
- **Backend:** holdings + settings endpoints (base currency = EUR), user-scoped.
- **Frontend:** holdings list + add/edit form (fund by ISIN, gold in grams), settings.
- **Done when:** a user can add/edit/remove holdings and they persist per-user.

### 05 Market-data layer + automated valuation
- **Backend:** `MarketDataProvider` interface + impls (gold spot + FX automated; fund NAV best-effort; manual fallback); APScheduler job writing `price_snapshots`, `fx_rates`, `portfolio_snapshots`; manual trigger endpoint.
- **Done when:** running the job values the seeded portfolio in EUR and stores a daily snapshot. (Provider = ADR-0001.)

### 06 Dashboard — real data
- **Both:** wire dashboard to real holdings + valuations via the API.
- **Done when:** dashboard shows real current value and allocation.

## Phase 3 — Transactions & Returns

### 07 Transactions
- **Both:** transactions endpoints + UI (buy/sell/dividend/fee); update holding quantity + average cost.
- **Done when:** adding transactions correctly updates cost basis and quantity.

### 08 Returns engine
- **Backend:** period-return calculation from `portfolio_snapshots` (current vs start-of-period).
- **Done when:** D/W/M/Y returns are correct against a known snapshot series.

## Feature Count

| Phase | Features |
| ----- | -------- |
| Phase 0 — Scaffolding | 1 |
| Phase 1 — Foundation | 3 |
| Phase 2 — Holdings & Valuation | 3 |
| Phase 3 — Transactions & Returns | 2 |
| **Total** | **9** |
