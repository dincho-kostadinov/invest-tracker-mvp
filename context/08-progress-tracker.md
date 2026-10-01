# Progress Tracker

## Current Status

**Phase:** Phase 1 — Foundation
**Last completed:** 02 Database schema: 7 new tables (`accounts`, `assets`,
`holdings`, `transactions`, `price_snapshots`, `fx_rates`, `portfolio_snapshots`)
plus migration `173a1a8fecf2`, with exact numerics (ADR-0003) and per-user
assets with DB-enforced ownership (ADR-0004). Idempotent seed
`uv run python -m app.seed` creates `demo@investtracker.example` from the
gitignored `backend/seed_data.json` (the owner's real positions), falling back
to the committed `seed_data.example.json`. 30/30 backend pytest, ruff/mypy
clean. See `specs/02-database-schema.md`.
**In progress:** —
**Next:** 03 Dashboard UI (mock data). Run `/architect` to write its spec.

## Progress

### Phase 0 — Scaffolding
- [x] 00 Monorepo + skeletons

### Phase 1 — Foundation
- [x] 01 Auth + app shell
- [x] 02 Database schema
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
- 2026-09-24 — 01 Auth + app shell built: session cookie is set by the **frontend** (Route Handlers), not the backend — see `01-architecture.md`'s Authentication section for why (cross-origin cookie visibility). Auth = Authlib (OAuth client + JWT) + `bcrypt` directly (not `passlib` — broken against modern `bcrypt`, see spec). Google OAuth's redirect roundtrip stays on the backend's own origin, then hands off to the frontend via a short-lived one-time exchange code (in-memory, MVP-only). `users` table + first Alembic migration added in this feature (ahead of 02, since login needs it). shadcn/ui installed by hand (no interactive CLI) with only the 3 button variants `06-ui-rules.md` defines. Discovered Next.js 16 renamed `middleware.ts` to `proxy.ts` — see `04-library-docs.md`.
- 2026-09-28 — `/review` on 01 found 7 issues (2 Important + 1 Minor system-integrity, 3 Important + 3 Minor production-readiness); all fixed and re-verified (10/10 backend pytest, ruff/mypy/eslint/tsc clean, 1/1 e2e). Worth remembering: (1) Google sign-in now requires `userinfo.email_verified` before auto-linking to an existing email/password account by email match — un-checked, that's a real account-takeover pattern. (2) bcrypt's limit is 72 **bytes**, not characters — a password well under any char-count limit can still crash it via multi-byte UTF-8 (emoji); both `SignupRequest` (backend) and the frontend's `/api/auth/signup` Route Handler now validate byte length, and `verify_password`/`hash_password` guard it too since a public Route Handler can't rely on the React form's client-side check alone. (3) Login always runs one bcrypt comparison now, even for a nonexistent email, to avoid a timing side-channel that would otherwise leak which emails are registered.
- 2026-09-30 — 02 Database schema built. ADR-0003 (Accepted): amounts stay integer minor units; unit prices, quantities and FX rates are exact `NUMERIC`/`Decimal`; holdings store `cost_basis_minor` (total invested), not a per-unit average, because real platform data showed avg × qty ≠ invested sum. ADR-0004 (Accepted): assets are per-user; composite FKs on `(parent_id, user_id)` make cross-user links impossible in the DB. Worth remembering: (1) "refuse delete while referenced" FKs are `NO ACTION`, not `RESTRICT`, because `RESTRICT` breaks the user-delete cascade in Postgres. (2) Enumerations are `VARCHAR` + `CHECK`, not native `ENUM`. (3) The seed validates that each holding's BUYs sum exactly to its quantity and cost basis, and writes nothing if they don't.

## Notes

- First user's holdings: Amundi funds, Schroders funds, physical 24k gold.
- Hosting target not yet chosen (future ADR).
- Design is light-theme only for MVP; a dark theme is a token-swap (add `.dark` block) if wanted later.
