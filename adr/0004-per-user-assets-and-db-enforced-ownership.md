# ADR-0004 — Per-user assets and database-enforced ownership

Status: Accepted
Date: 2026-09-30
Deciders: Dincho
Related: specs/02-database-schema.md, context/01-architecture.md, context/04-library-docs.md

## Context

The first-cut data model had `assets` as a **global catalogue** (no `user_id`),
shared by every user holding the same instrument. That conflicts with how the
app is meant to be used: each user defines their own funds, gold, and stocks,
and the MVP's **manual price fallback** means a price one user types in must
never change another user's valuation.

Separately, `holdings` and `transactions` carry a `user_id` **and** point at
parent rows (`accounts`, `assets`, `holdings`) that also carry a `user_id`. With
plain foreign keys, nothing in the database stops a row owned by user A from
referencing user B's account or asset. The invariant "every query is scoped to
the current user — no cross-user access, ever" would then rest entirely on
every future feature remembering an ownership check.

## Decision

We will:

1. **Make `assets` per-user**: `assets.user_id` (FK → `users`), with a partial
   unique index on `(user_id, isin) WHERE isin IS NOT NULL`. Price history
   (`price_snapshots`) hangs off the asset, so it is per-user by inheritance.
   `fx_rates` stays **global** (a market fact, identical for everyone).
2. **Enforce ownership with composite foreign keys**:
   - `accounts`, `assets`, `holdings` each get a `UNIQUE (id, user_id)`.
   - `holdings (account_id, user_id)` → `accounts (id, user_id)`
   - `holdings (asset_id, user_id)` → `assets (id, user_id)`
   - `transactions (holding_id, user_id)` → `holdings (id, user_id)`

   A cross-user link is then impossible at the database level, regardless of
   application code.

## Alternatives considered

- **Global asset catalogue** (original model) — rejected: users can't define
  their own assets, and a manual price would leak across users.
- **Plain FKs + application-level ownership checks** — rejected: simpler, but a
  single forgotten check in a future feature becomes a silent cross-user leak.
- **Postgres Row-Level Security** — deferred: strong, but needs a per-request DB
  role/session variable plumbing that the MVP doesn't otherwise need.

## Consequences

- Easier: cross-user corruption is structurally impossible; per-user manual
  prices are naturally isolated.
- Harder: the same ISIN held by two users is two `assets` rows. The valuation job
  (feature 05) should fetch each distinct ISIN **once** and write the price to
  every matching asset, to avoid duplicate provider calls.
- Inserts into `holdings` / `transactions` must supply the correct `user_id`
  (they already must, for query scoping) — a mismatch now fails loudly with an
  `IntegrityError` instead of silently succeeding.
- One extra unique constraint per parent table.

## Follow-up — reflect this decision in the living context

- [x] `context/01-architecture.md` — data model table (`assets.user_id`) + Invariants (DB-enforced ownership)
- [x] `context/04-library-docs.md` — SQLAlchemy section: composite FK pattern for user-owned children
