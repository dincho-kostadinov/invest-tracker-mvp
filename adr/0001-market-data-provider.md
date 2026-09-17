# ADR-0001 — Market-data provider for fund NAV, gold spot, and FX

Status: Proposed
Date: 2026-09-17
Deciders: Dincho
Related: context/01-architecture.md, context/04-library-docs.md

## Context

Valuation is the core of the app and its biggest external risk. The first
user's holdings are **Amundi funds**, **Schroders funds**, and **physical 24k
gold**, valued in a **EUR** base. That needs three data types:

- **Fund NAV by ISIN** (Amundi, Schroders) — daily. Free coverage of EU
  mutual funds by ISIN is spotty; many free APIs cover US stocks/ETFs but not
  EU mutual-fund NAVs.
- **Gold spot** (XAU) → price per gram in EUR.
- **FX rates** (e.g. USD→EUR) to convert non-EUR prices.

No single free provider cleanly covers all three, so the choice must not be
hard-wired into the app.

## Decision

Define a `MarketDataProvider` interface in `lib/marketdata/` with methods for
`getFundNav(isin)`, `getGoldSpot()`, and `getFxRate(base, quote)`. The app
depends on the interface, not a vendor.

MVP ships with:
- **Gold spot + FX** from a free provider (candidates: metals API for XAU,
  ECB / exchangerate.host for FX) — automated.
- **Fund NAV** from the best available free source per ISIN; where none covers a
  fund, a **manual price entry** fallback keeps that asset valued.

The concrete providers are selected after a short spike (see Consequences) and
this ADR is then moved to `Accepted` with the chosen vendors named.

## Alternatives considered

- **Hard-code one vendor** — rejected: no free vendor covers EU fund NAV + gold + FX.
- **Manual prices only** — rejected: defeats the "automated valuation" goal.
- **Paid aggregation (e.g. broker APIs)** — deferred: cost/complexity beyond MVP.

## Consequences

- A time-boxed **spike** is needed to confirm which free source returns Amundi
  and Schroders NAV by ISIN, and gold spot in EUR. This spike gates finalizing this ADR.
- The provider interface + manual fallback means the app works even if a fund
  isn't covered.
- Rate limits / caching must be handled in `lib/marketdata`.

## Follow-up — reflect this decision in the living context

- [ ] `context/01-architecture.md` — market-data row named once vendors chosen
- [ ] `context/04-library-docs.md` — usage section for the chosen client(s)
- [ ] Move status to `Accepted` after the spike
