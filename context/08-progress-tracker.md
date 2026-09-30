# Progress Tracker

## Current Status

**Phase:** Phase 1 — Foundation
**Last completed:** 01 Auth + app shell — backend JWT auth (Google OAuth +
email/password) via Authlib, `/me`, `get_current_user` dependency, `users`
table + first Alembic migration; frontend login/signup pages, app shell nav,
`proxy.ts` route protection, session cookie owned by the frontend (see
`specs/01-auth-app-shell.md`). shadcn/ui wired in as the first real UI
feature. `/review` found 7 issues (account-linking security gap, a bcrypt
crash on overlong passwords, and 5 smaller ones) — all fixed and re-verified.
Fully verified end-to-end including a real Google OAuth round trip with the
developer's own Cloud OAuth client (2026-09-30) — every "Done when" box in
the spec is now checked. 10/10 backend pytest, 1/1 Playwright e2e, ruff/
mypy/eslint/tsc all clean.
**In progress:** —
**Next:** 02 Database schema (run `/architect` to write its spec)

## Progress

### Phase 0 — Scaffolding
- [x] 00 Monorepo + skeletons

### Phase 1 — Foundation
- [x] 01 Auth + app shell
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
- 2026-09-24 — 01 Auth + app shell built: session cookie is set by the **frontend** (Route Handlers), not the backend — see `01-architecture.md`'s Authentication section for why (cross-origin cookie visibility). Auth = Authlib (OAuth client + JWT) + `bcrypt` directly (not `passlib` — broken against modern `bcrypt`, see spec). Google OAuth's redirect roundtrip stays on the backend's own origin, then hands off to the frontend via a short-lived one-time exchange code (in-memory, MVP-only). `users` table + first Alembic migration added in this feature (ahead of 02, since login needs it). shadcn/ui installed by hand (no interactive CLI) with only the 3 button variants `06-ui-rules.md` defines. Discovered Next.js 16 renamed `middleware.ts` to `proxy.ts` — see `04-library-docs.md`.
- 2026-09-28 — `/review` on 01 found 7 issues (2 Important + 1 Minor system-integrity, 3 Important + 3 Minor production-readiness); all fixed and re-verified (10/10 backend pytest, ruff/mypy/eslint/tsc clean, 1/1 e2e). Worth remembering: (1) Google sign-in now requires `userinfo.email_verified` before auto-linking to an existing email/password account by email match — un-checked, that's a real account-takeover pattern. (2) bcrypt's limit is 72 **bytes**, not characters — a password well under any char-count limit can still crash it via multi-byte UTF-8 (emoji); both `SignupRequest` (backend) and the frontend's `/api/auth/signup` Route Handler now validate byte length, and `verify_password`/`hash_password` guard it too since a public Route Handler can't rely on the React form's client-side check alone. (3) Login always runs one bcrypt comparison now, even for a nonexistent email, to avoid a timing side-channel that would otherwise leak which emails are registered.

## Notes

- First user's holdings: Amundi funds, Schroders funds, physical 24k gold.
- Hosting target not yet chosen (future ADR).
- Design is light-theme only for MVP; a dark theme is a token-swap (add `.dark` block) if wanted later.
