# Memory — Feature 01: Auth + App Shell

Last updated: 2026-09-30

## What was built

- Backend: JWT auth (Authlib) + Google OAuth + email/password.
  `app/core/security.py` (bcrypt hash/verify, JWT via `joserfc`, 72-byte
  guard), `app/core/oauth.py` (Authlib Google client, in-memory one-time
  exchange-code store), `app/api/deps.py` (`get_current_user`),
  `app/api/auth.py` (signup/login/google-login/google-callback/exchange/me),
  `app/schemas/auth.py`, `app/models/{base,user}.py`, first Alembic
  migration (`users` table). `app/main.py` wired with `SessionMiddleware` +
  CORS `allow_credentials`.
- Frontend: shadcn/ui installed by hand (`components.json`, `globals.css`
  tokens, `lib/utils.ts`), primitives in
  `components/ui/{button,input,label,card,separator,avatar}.tsx`. Auth pages
  `app/(auth)/{login,signup}/page.tsx` + shared
  `components/auth/auth-form.tsx`. Route Handlers
  `app/api/auth/{login,signup,logout}/route.ts` + Google callback
  `app/auth/callback/route.ts`. `proxy.ts` (Next 16 renamed `middleware.ts`)
  gates `(app)` routes. App shell `app/(app)/layout.tsx` + nav
  (`components/nav/nav-link.tsx`) + placeholder pages
  (dashboard/holdings/transactions/settings) + `error.tsx` boundary.
  `lib/auth/{constants,session}.ts`, `lib/api/auth.ts`, `lib/api/client.ts`
  (added `apiPost`, exported `API_BASE_URL`). One Playwright e2e
  (`e2e/auth.spec.ts`) + config.
- Spec: `specs/01-auth-app-shell.md` — Status: Built, every "Done when" box
  checked.

## Decisions made

- **Frontend owns the httpOnly session cookie, not the backend** —
  cross-origin visibility problem (`proxy.ts` / `next/headers` can't see a
  cookie set by the backend's own origin). Backend `/auth/*` is plain JSON
  `{access_token}`; Next.js Route Handlers set the cookie. Documented in
  `01-architecture.md`.
- **Google OAuth stays same-origin on the backend, then hands off via a
  one-time exchange code** (in-memory, ~60s TTL) to the frontend's
  `/auth/callback` Route Handler — required because Authlib's state/nonce
  check needs `/authorize` and `/callback` on the same origin.
- Auth = Authlib (OAuth client + JWT via `joserfc`) + `bcrypt` directly — not
  `passlib` (broken against `bcrypt>=4.1`), not `python-jose`.
- No `app/domain/auth.py` — signup/login do their own simple SQLAlchemy
  queries directly in the router, matching the `health.py` precedent
  (`domain/` stays framework-free, reserved for real business logic like
  valuation later).
- `users` table built in *this* feature (not 02), since login needs it.

## Problems solved

- passlib's bcrypt backend crashes against modern `bcrypt`
  (`AttributeError: module 'bcrypt' has no attribute '__about__'`) —
  switched to `bcrypt` directly.
- bcrypt's limit is 72 **bytes**, not characters — a password under any
  char-count limit can crash `hashpw`/`checkpw` via multi-byte UTF-8
  (emoji). Fixed with byte-length validation at both the Pydantic schema and
  the frontend Route Handler (it's a public endpoint too, can't rely on the
  React form's client-side check alone), plus defensive guards in
  `security.py` itself.
- Next.js 16 renamed `middleware.ts` → `proxy.ts` (exported function name
  `proxy`, not `middleware`); `error.tsx`'s second prop is now `retry`, not
  `reset`. Found by reading `node_modules/next/dist/docs/` before writing
  routing code, per `frontend/AGENTS.md`'s warning that this Next version
  has training-data-breaking changes.
- `/review` found a real account-takeover pattern: Google sign-in was
  auto-linking to an existing email/password account by email match with no
  `email_verified` check — fixed.
- `/review` also found a login timing side-channel (nonexistent-email logins
  returned faster than wrong-password ones) — fixed by always running one
  bcrypt comparison via a dummy hash.
- Google Cloud Console's OAuth client needs the *exact* redirect URI
  `http://localhost:8000/auth/google/callback` registered
  (scheme/host/port/trailing-slash all must match). Hit a
  `redirect_uri_mismatch` the first time — fixed in the Console, not code.

## Active spec

`specs/01-auth-app-shell.md` — Status: **Built**. Every "Done when" box
checked, including a real Google OAuth round trip verified manually against
the developer's own Google Cloud OAuth client (2026-09-30).

## Current state

- Everything works and is verified: 10/10 backend pytest, 1/1 Playwright
  e2e, ruff/mypy/eslint/tsc all clean. Manually verified end-to-end:
  email/password signup/login/logout, redirect-when-unauthenticated, and —
  as of this session — real Google sign-in.
- `backend/.env` has real `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET` from the
  developer's own Google Cloud project (gitignored, not committed).
  `.env.example` stays blank as a template.
- Context files updated: `01-architecture.md` (Authentication section),
  `03-code-standards.md` + `04-library-docs.md` (new deps, the bcrypt
  byte-limit note, the OAuth email-verified note), `07-ui-registry.md`
  (imprinted: Button/Input/Label/Card/Separator/Avatar/app-shell-nav/
  placeholder), `08-progress-tracker.md` (01 marked done).
- **Nothing has been committed yet** — the developer said they'll commit it
  themselves.
- Dev servers stopped, Docker containers torn down (the Postgres data volume
  persists — it now holds one real user record from the developer's own
  Google sign-in test).

## Next session starts with

`/architect` for **"02 Database schema"**: SQLAlchemy models for the
remaining tables in `01-architecture.md` (`accounts`, `assets`, `holdings`,
`transactions`, `price_snapshots`, `fx_rates`, `portfolio_snapshots`) onto
the same `Base` feature 01 created, + an Alembic migration + a seed script
with the owner's sample holdings (Amundi/Schroders funds + gold). See
`context/02-build-plan.md`.

## Open questions

- None from feature 01. CI still hasn't been exercised by an actual push
  (carried over from feature 00) — worth confirming whenever this branch/PR
  first goes up.
