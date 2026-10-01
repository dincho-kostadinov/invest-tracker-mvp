# Spec — Database schema

Status: Built
Created: 2026-09-30   ·   Last updated: 2026-09-30
Phase / Feature: Phase 1 · 02

> Written by /architect, confirmed by the developer before any code.
> /review checks the built feature against this file.

## What we are building

SQLAlchemy models and one Alembic migration for the remaining seven tables of
the data model — `accounts`, `assets`, `holdings`, `transactions`,
`price_snapshots`, `fx_rates`, `portfolio_snapshots` — on the existing `Base`
from feature 01, with exact numeric types (ADR-0003), per-user assets and
database-enforced ownership (ADR-0004), and explicit delete rules. Plus an
idempotent seed script that creates a demo user with the owner's portfolio shape
(1 Schroders fund, 2 Amundi funds, physical gold), reading real values from a
gitignored JSON file and falling back to a committed example file. No API
endpoints, no UI.

## Language we agreed on

- **Asset**: an instrument **one user** defined (fund by ISIN, gold, stock) —
  per-user, has `user_id`. Two users holding the same ISIN have two asset rows.
  Carries kind, name, optional ISIN/symbol, currency, and unit (`share`|`gram`).
- **Account**: a platform/place where a user keeps assets (e.g. "Amundi",
  "Schroders", "Home safe") — not a login, not a bank account. Owned by one user.
- **Holding**: one user's position in one asset at one account, unique per
  (account, asset). Stores current `quantity` and total `cost_basis_minor`. Can
  exist without transactions (manual entry in 04); feature 07 will maintain it
  from transactions.
- **Quantity**: number of units of the asset's `unit` — always allowed to be
  fractional (`NUMERIC(20,8)`). Not money.
- **Amount** vs **price**: an *amount* is a sum of money → integer minor units
  (`_minor`, `BIGINT`). A *price* is per-unit → `NUMERIC(20,6)`. (ADR-0003)
- **as_of**: a calendar **DATE** (not a timestamp) on `price_snapshots`,
  `fx_rates`, `portfolio_snapshots` — one row per asset / pair / user per day.
- **Seed**: an idempotent, manually-run script (`uv run python -m app.seed`)
  that creates the demo user and their portfolio. Not a migration.

## Decisions made

- **Exact numerics (ADR-0003)**: amounts = `BIGINT` minor units + currency;
  quantity and FX rate = `NUMERIC(20,8)`; unit prices = `NUMERIC(20,6)`; Python
  `Decimal`, never `float`.
- **Holdings store `cost_basis_minor` (total invested), not `avg_cost_minor`**
  (ADR-0003): real platform data showed avg × qty ≠ invested sum (5 018.76 vs
  5 019.14 EUR). Average cost is derived.
- **Transactions store both `price` (NUMERIC, nullable) and `amount_minor`**
  (cash moved, BIGINT) plus `fee_minor` — same reason. `price`/`quantity` are
  nullable because DIVIDEND and FEE have no unit price or quantity.
- **Assets are per-user (ADR-0004)**, partial unique `(user_id, isin) WHERE isin
  IS NOT NULL`. `fx_rates` is global.
- **Composite FKs enforce ownership (ADR-0004)**: `UNIQUE (id, user_id)` on
  `accounts`/`assets`/`holdings`; children reference `(parent_id, user_id)`.
- **Delete rules**:
  | Delete | Effect |
  |---|---|
  | user | `CASCADE` to accounts, assets, holdings, transactions, portfolio_snapshots (and via assets → price_snapshots) |
  | account / asset still referenced by a holding | refused (FK `NO ACTION`) |
  | asset | `CASCADE` its price_snapshots |
  | holding | `CASCADE` its transactions |
  | holding / asset | never touches portfolio_snapshots (historical totals) |

  *Build note:* "refused" is implemented as `NO ACTION`, not `RESTRICT`. Postgres
  checks `RESTRICT` immediately, so it can fail a user delete midway through the
  cascade (the account row goes before its holdings do). `NO ACTION` is checked
  at the end of the statement: a standalone account or asset delete is still
  refused, and a user delete cascades cleanly. Both behaviours are covered by
  tests.
- **Enumerations as `VARCHAR` + `CHECK` constraint**, backed by Python
  `StrEnum`s — not native Postgres `ENUM` (painful to extend in Alembic).
  - `accounts.type`: `fund_platform` | `broker` | `physical`
  - `assets.kind`: `FUND` | `GOLD` | `STOCK`
  - `assets.unit`: `share` | `gram`
  - `transactions.type`: `BUY` | `SELL` | `DIVIDEND` | `FEE`
- **Primary keys are UUID** (`Uuid`, `default=uuid.uuid4`), matching `users`.
- **Currency** columns are `CHAR(3)` ISO 4217 codes.
- **Uniqueness**: `accounts (user_id, name)`; `holdings (account_id, asset_id)`;
  `price_snapshots (asset_id, as_of)`; `fx_rates (as_of, base, quote)`;
  `portfolio_snapshots (user_id, as_of)`.
- **Seed user is a separate demo user** `demo@investtracker.example`, password
  login, password from env `SEED_DEMO_PASSWORD` (never hardcoded). Never touches
  the owner's real Google-login account.
  *Build note:* originally `demo@investtracker.local`. `email-validator` rejects
  special-use domains (`.local`, `.test`), so that user could never log in.
  Changed to the reserved `.example` TLD; `test_demo_email_passes_login_validation`
  guards it.
- **Seed data lives in JSON**: real positions in gitignored
  `backend/seed_data.json`; committed `backend/seed_data.example.json` with dummy
  values in the same shape. Script uses the real file if present, else the
  example. Validated with Pydantic on load.
- **Seed is idempotent**: if the demo user already exists, it logs and exits
  without changes.
- **Seed writes BUY transactions from the JSON** so feature 07 starts from
  consistent data: each holding lists its purchases (quantity, amount, date);
  price = amount / quantity. A holding's quantity and cost basis must equal the
  sum of its BUYs — the seed validates this on load and refuses mismatched data.
  Funds have one BUY each (real purchase dates unknown); gold has its 4 real
  purchases.
  **No price/FX/portfolio snapshots** — those come from the real job in 05.

## Table shapes

(All tables also get `created_at TIMESTAMPTZ DEFAULT now()`; mutable ones
`holdings`/`accounts`/`assets` also `updated_at`.)

- **accounts**: id, user_id → users, name `VARCHAR(100)`, type
- **assets**: id, user_id → users, kind, name `VARCHAR(200)`, isin `VARCHAR(12)`?,
  symbol `VARCHAR(20)`?, currency, unit
- **holdings**: id, user_id, account_id, asset_id, quantity `NUMERIC(20,8)`,
  cost_basis_minor `BIGINT`, currency
- **transactions**: id, user_id, holding_id, type, quantity `NUMERIC(20,8)`?,
  price `NUMERIC(20,6)`?, amount_minor `BIGINT`, fee_minor `BIGINT DEFAULT 0`,
  currency, occurred_at `TIMESTAMPTZ`
- **price_snapshots**: id, asset_id → assets, as_of `DATE`, price `NUMERIC(20,6)`,
  currency, source `VARCHAR(50)` (`manual` or provider name)
- **fx_rates**: id, as_of `DATE`, base `CHAR(3)`, quote `CHAR(3)`, rate `NUMERIC(20,8)`
- **portfolio_snapshots**: id, user_id → users, as_of `DATE`,
  total_value_minor `BIGINT`, base_currency `CHAR(3)`

## Seed data (real file — `backend/seed_data.json`, gitignored)

| Account (type) | Asset (kind, unit) | ISIN | Quantity | Cost basis |
|---|---|---|---|---|
| Schroders (fund_platform) | SISF Global Sustainable Growth EUR (FUND, share) | LU0557291076 | 12.35 | 4 749.89 EUR |
| Amundi (fund_platform) | AF US Equity Fundamental Growth – EUR (FUND, share) | LU1883854199 | 7.569 | 4 520.46 EUR |
| Amundi (fund_platform) | AF US Pioneer Fund – EUR (FUND, share) | LU1883872332 | 181.905 | 5 019.14 EUR |
| Home safe (physical) | Gold 24k (GOLD, gram) | — | 14.5 | 1 695.21 EUR |

Gold BUY transactions (real dates; sum = 14.5 g / 1 695.21 EUR):

| occurred_at | Quantity (g) | Amount | Derived price / g |
|---|---|---|---|
| 2024-11-29 | 2.5 | 243.37 EUR | 97.348 |
| 2025-03-12 | 1 | 109.93 EUR | 109.93 |
| 2025-11-08 | 10 | 1 195.91 EUR | 119.591 |
| 2026-06-23 | 1 | 146.00 EUR | 146.00 |

## Assumptions

- Gold is held in an account named **"Home safe"** (`physical`), in EUR — rename
  in the JSON if wrong.
- All seeded assets and holdings are in EUR.
- Fund BUY transactions use `occurred_at` from the JSON; real fund purchase
  dates aren't known, so the real file uses a single placeholder date per fund
  (editable later). Gold uses its 4 real purchase dates.
- Tests run against the local Docker Postgres, as in feature 01; test data is
  cleaned up by deleting the test user (cascade).
- No new libraries are needed (SQLAlchemy `Numeric`, stdlib `decimal`/`json`).

## Scope

**In scope:**
- 7 SQLAlchemy models + `StrEnum`s in `backend/app/models/`
- One Alembic migration creating them (with downgrade)
- Seed script `backend/app/seed.py`, `seed_data.example.json`, gitignore entry
- pytest tests for constraints, delete rules, and seed idempotency
- ADR-0003, ADR-0004 → Accepted; context files updated

**Out of scope:**
- Any API endpoint, Pydantic request/response schemas for these tables, or UI
- Domain logic (valuation, cost-basis updates, returns) — features 05/07/08
- Price/FX/portfolio snapshot data
- Soft deletes, Row-Level Security, a user base-currency setting (04)

## How to build it

1. Mark ADR-0003/0004 Accepted; update `01-architecture.md` (data model table,
   invariants), `03-code-standards.md` (Money & Numbers),
   `04-library-docs.md` (SQLAlchemy: `Numeric` → `Decimal`, composite-FK pattern).
2. `app/models/enums.py` — `AccountType`, `AssetKind`, `AssetUnit`,
   `TransactionType` (`StrEnum`) + a helper to build the `CHECK` constraint.
3. One model file per table in `app/models/` (`account.py`, `asset.py`,
   `holding.py`, `transaction.py`, `price_snapshot.py`, `fx_rate.py`,
   `portfolio_snapshot.py`); export from `app/models/__init__.py`.
4. `uv run alembic revision --autogenerate -m "create portfolio tables"`;
   hand-check the generated file: composite FKs, `ondelete` rules, CHECK
   constraints, partial unique index on `assets`, NUMERIC precision/scale,
   and a clean downgrade.
5. `alembic upgrade head` → `downgrade -1` → `upgrade head` on the dev DB.
6. `backend/seed_data.example.json` (dummy values, same shape) and gitignored
   `backend/seed_data.json` (real values from the table above); add
   `backend/seed_data.json` to `.gitignore`.
7. `app/seed.py` — load JSON (real → example fallback), validate with Pydantic,
   read `SEED_DEMO_PASSWORD` via settings, create demo user + accounts + assets +
   holdings + one BUY each in a single DB transaction; skip if demo user exists.
   Add `SEED_DEMO_PASSWORD` to `.env.example` and the env table in
   `03-code-standards.md`.
8. Tests in `backend/tests/test_schema.py` and `test_seed.py` (see Done when).
9. ruff, mypy, full pytest; update `08-progress-tracker.md`.

## Done when

- [x] When `alembic upgrade head` runs on an empty database, the system shall create all 8 tables with no errors; `alembic downgrade -1` followed by `upgrade head` shall also succeed.
- [x] When a holding is inserted whose `user_id` differs from its account's or asset's `user_id`, the database shall reject it with an `IntegrityError`. (test)
- [x] When a transaction is inserted whose `user_id` differs from its holding's `user_id`, the database shall reject it. (test)
- [x] When a user is deleted, the system shall delete all their accounts, assets, holdings, transactions, price snapshots and portfolio snapshots. (test)
- [x] When an account or asset still referenced by a holding is deleted, the database shall refuse the delete. (test)
- [x] When a holding is deleted, its transactions shall be deleted too. (test)
- [x] When an asset, account type, or transaction type outside the allowed values is inserted, the database shall reject it. (test)
- [x] When the same user creates two assets with the same ISIN, the database shall reject the second; two different users with the same ISIN shall both succeed. (test)
- [x] When quantity 181.905 and price 27.593237 are stored and read back, the values shall be `Decimal`s equal to what was written. (test)
- [x] When the seed runs on a database without the demo user, the system shall create `demo@investtracker.example` with 3 accounts, 4 assets, 4 holdings and 7 BUY transactions (1 per fund + 4 gold) matching the JSON. (test)
- [x] When the seed JSON has a holding whose quantity or cost basis doesn't equal the sum of its BUYs, the seed shall refuse to run and change nothing. (test)
- [x] When the seed runs a second time, the system shall make no changes. (test)
- [x] When `backend/seed_data.json` is absent, the seed shall use `seed_data.example.json`; the real file shall be gitignored.
- [x] When the demo user logs in through the existing auth with `SEED_DEMO_PASSWORD`, login shall succeed. (verified via `/auth/login` + `/me`; test guards the email)
- [x] ruff, mypy, and the full pytest suite pass; ADR-0003/0004 Accepted and context files updated.

## Open questions

- None. (Real fund purchase dates can be added to `seed_data.json` later —
  the seed just needs each holding's BUYs to sum to its quantity and cost.)
