# Progress Tracker

## Current Status

**Phase:** Phase 1 — Foundation
**Last completed:** 00 Monorepo + skeletons — `backend/` (FastAPI + uv) and
`frontend/` (Next.js + npm) scaffolded per `specs/00-monorepo-skeletons.md`;
Postgres via Docker Compose; `/health` verified end-to-end both natively and
via full `docker compose up` (backend/frontend Dockerfiles); CI running
lint + type-check for both apps.
**In progress:** —
**Next:** 01 Auth + app shell (run `/architect` to write its spec)

## Progress

### Phase 0 — Scaffolding
- [x] 00 Monorepo + skeletons

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
- 2026-09-17 — 00 Monorepo + skeletons built: Postgres via Docker Compose is the daily-dev default (DB only, apps run natively for hot reload); `backend/Dockerfile` + `frontend/Dockerfile` added and wired into `docker-compose.yml` so `docker compose up` alone also runs the full stack. Python deps via `uv`, Node deps via `npm`. Frontend's typed API client is a hand-rolled minimal fetch wrapper for now — the OpenAPI-generated client (per `04-library-docs.md`) is deferred to 01, once there's more than one route.

## Notes

- First user's holdings: Amundi funds, Schroders funds, physical 24k gold.
- Hosting target not yet chosen (future ADR).
- Design is light-theme only for MVP; a dark theme is a token-swap (add `.dark` block) if wanted later.
