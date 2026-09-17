# Project Overview

## About the Project

**Invest Tracker** — a multi-user web app that unifies a person's investments
that live across different platforms (funds, physical gold, and later stocks)
into one portfolio, and shows how it performs over time.

## The Problem It Solves

Holdings are scattered across separate platforms, each with its own login and
view. There is no single place that shows total value and whether the portfolio
is up or down over a chosen period. Invest Tracker aggregates everything and
reports daily, weekly, monthly, and yearly return or loss.

## Target User

Individual retail investors who hold assets across multiple platforms (first
user: the owner). Multi-user hosted — each user sees only their own data.

## Pages

- **Auth** — sign up / log in
- **Dashboard** — total value, total P/L, returns by period (day/week/month/year), allocation
- **Holdings** — list, add/edit; per-asset detail with its history
- **Transactions** — buys / sells / dividends / fees
- **Settings** — base currency, connected platforms, profile

## Core User Flow

Sign up → add holdings (manual entry; automatic where a platform exposes an API)
→ the app values them from market data (fund NAV, gold spot, FX) → the dashboard
shows total value, allocation, and return/loss per period.

## Data Overview

Users own Accounts (platforms). Each Holding ties an Asset (a fund, gold, or
stock) to an Account with a quantity and cost. Prices and FX are fetched into
snapshots; a daily portfolio snapshot powers time-based returns. Full schema in
`01-architecture.md`.

## Features In Scope (MVP)

- Manual holdings CRUD (funds by ISIN, physical gold in grams; stocks supported by the model)
- **Automated valuation sync** — fetch fund NAV + gold spot + FX on a schedule
- Multi-currency holdings converted to a base currency (EUR for MVP)
- Returns per period: day, week, month, year
- Allocation breakdown (by asset type and by platform)
- Auth + strict per-user data isolation
- Manual price fallback for any asset the market-data provider can't cover

## Features Out of Scope (MVP)

- Automated broker/position aggregation for platforms without an API (physical gold and these funds are manual-position by nature)
- Trade execution, tax reporting, AI analysis/alerts, mobile app

## Success Criteria

- A user can add holdings and see the correct current total value in EUR.
- The dashboard shows correct P/L and returns for day, week, month, and year.
- Fund NAV, gold spot, and FX refresh automatically on schedule.
- Every user sees only their own data.
