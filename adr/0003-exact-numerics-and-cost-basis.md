# ADR-0003 — Exact numerics: NUMERIC for rates/prices/quantities, integer minor units for amounts

Status: Accepted
Date: 2026-09-30
Deciders: Dincho
Related: specs/02-database-schema.md, context/01-architecture.md, context/03-code-standards.md, context/04-library-docs.md

## Context

The original invariant says money is stored as **integer minor units + a
currency code**, never a float. That fits amounts (costs, fees, values), but
the real data this app handles does not all fit in cents:

- **Fund NAV per share** is published with 2–4+ decimals (e.g. 376.28,
  656.75, 29.10 today; other funds publish 123.4567). Rounding a unit price to
  cents and then multiplying by quantity compounds the error.
- **Quantity** is fractional: 12.35 / 7.569 / 181.905 fund shares, 14.5 g gold.
- **FX rates** (e.g. 1.08432) are ratios, not money.
- **Gold** is priced per gram from a per-troy-ounce spot price — a division
  that never comes out even.

The owner's own platform data also showed that a **per-unit average cost is a
lossy display value**: 181.905 shares × 27.59 EUR avg = 5 018.76 EUR, but the
platform's exact invested sum is 5 019.14 EUR. The total invested is the exact
figure; the average price is derived and rounded.

Storing everything as scaled integers (e.g. price × 10⁶ in `BIGINT`) would keep
"integer only" but makes every read/write depend on remembering a scale factor —
a forgotten conversion is a silent 10⁶× error.

## Decision

We will use two tiers of exact representation — **never `float`** anywhere:

1. **Amounts** (a sum of money: cost basis, transaction cash amount, fee,
   portfolio total value) stay **integer minor units (`BIGINT`) + a currency
   code**. Column suffix `_minor`.
2. **Unit prices, quantities, and FX rates** are **Postgres `NUMERIC`** with a
   fixed scale, mapped to Python **`Decimal`**:
   - quantity: `NUMERIC(20, 8)`
   - unit price (NAV, gold per gram, transaction price): `NUMERIC(20, 6)`
   - FX rate: `NUMERIC(20, 8)`
3. A holding stores its **total cost basis** (`cost_basis_minor`), not a per-unit
   average cost. Average cost is always derived: `cost_basis / quantity`.
4. Converting a computed value (quantity × price × rate) into an amount rounds
   **once**, in the backend `domain` layer (ROUND_HALF_EVEN to minor units),
   where it is unit-tested.

## Alternatives considered

- **Integer minor units for everything (prices in cents)** — rejected: loses NAV
  precision that the data source actually publishes; error multiplies by quantity.
- **Scaled integers (`BIGINT` × 10⁶) for prices/quantities/rates** — rejected:
  exact, but every boundary needs a scale conversion; forgetting one is a silent
  bug. NUMERIC + `Decimal` gives the same exactness with no scale bookkeeping.
- **Store `avg_cost_minor` per unit** (the original data model) — rejected: the
  average is a rounded, derived value; storing it drifts from the true invested
  sum (5 018.76 vs 5 019.14 EUR in real data).
- **`float` / `DOUBLE PRECISION`** — rejected outright: binary floating point is
  not acceptable for money.

## Consequences

- Easier: values are stored exactly as providers publish them; no scale-factor
  bugs; average cost is always consistent with the invested sum.
- Harder: Pydantic schemas and JSON responses must serialize `Decimal` carefully
  (as strings, or explicitly) so the frontend never parses them into a lossy
  JS `number` for arithmetic — the frontend only displays, never computes money.
- The single rounding point (value → minor units) lives in `domain` and must be
  covered by tests in features 05/08.
- Negligible performance cost of NUMERIC vs BIGINT at this app's scale.

## Follow-up — reflect this decision in the living context

- [x] `context/01-architecture.md` — Invariants (money rule) + data model table (`cost_basis_minor`, NUMERIC columns)
- [x] `context/03-code-standards.md` — "Money & Numbers" section
- [x] `context/04-library-docs.md` — SQLAlchemy section: `Numeric(..., asdecimal=True)` → `Decimal`
