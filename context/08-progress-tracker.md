# Progress Tracker

## Current Status

**Phase:** Phase 0 — Scaffolding
**Last completed:** context filled; ADR-0002 (Python/FastAPI); UI design approved → `05-ui-tokens.md` + `06-ui-rules.md` filled; designs in `context/designs/`
**In progress:** —
**Next:** 00 Monorepo + skeletons (run `/architect` to write its spec)

## Progress

### Phase 0 — Scaffolding
- [ ] 00 Monorepo + skeletons

### Phase 1 — Foundation
- [ ] 01 Auth + app shell
- [ ] 02 Database schema
- [ ] 03 Dashboard UI (mock data)

### Phase 2 — Holdings & Valuation
- [ ] 04 Holdings CRUD + Settings
- [ ] 05 Market-data layer + automated valuation
- [ ] 06 Dashboard — real data

### Phase 3 — Transactions & Returns
- [ ] 07 Transactions
- [ ] 08 Returns engine

## Decisions Made During Build

- 2026-09-17 — Base currency = EUR for MVP.
- 2026-09-17 — ADR-0001 (Proposed): market-data provider behind an interface; gold spot + FX automated, fund NAV best-effort with manual fallback. Needs a spike.
- 2026-09-17 — ADR-0002 (Accepted): split architecture — Next.js frontend + Python/FastAPI backend (monorepo); SQLAlchemy + Alembic; Pydantic; backend-owned JWT auth (Google + email).
- 2026-09-17 — "Auto-sync" in MVP = automated price/valuation; broker position import out of scope for these holdings.
- 2026-09-17 — UI design approved: shadcn/ui, light theme; indigo brand accent; emerald/red gain-loss; indigo+amber Funds/Gold. Tokens/rules derived; screenshots in `context/designs/`.

## Notes

- First user's holdings: Amundi funds, Schroders funds, physical 24k gold.
- Hosting target not yet chosen (future ADR).
- Design is light-theme only for MVP; a dark theme is a token-swap (add `.dark` block) if wanted later.
