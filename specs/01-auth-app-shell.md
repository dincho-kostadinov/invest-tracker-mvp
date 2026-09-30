# Spec — Auth + App Shell

Status: Built
Created: 2026-09-17   ·   Last updated: 2026-09-24
Phase / Feature: Phase 1 · 01

> Written by /architect, confirmed by the developer before any code.
> /review checks the built feature against this file.

## What we are building

Backend JWT auth (Google OAuth + email/password), a `/me` endpoint, and a
protected-route dependency; a frontend login + signup page, an authenticated
app shell (nav + layout), and middleware that redirects unauthenticated users
to `/login`. This is also the first feature with any real UI, so it lays down
the shadcn/ui + design-token plumbing (`globals.css`) every later UI feature
builds on.

## Language we agreed on

- **App shell**: the persistent authenticated layout (top nav with logo,
  Dashboard/Holdings/Transactions/Settings links, currency chip, avatar) that
  wraps every page under `(app)`.
- **Protected route**: a page that requires a valid session; unauthenticated
  visits redirect to `/login`.
- **Session**: a single long-lived (7-day) JWT, no refresh-token rotation.

## Decisions made

- **Both Google OAuth and email/password now**, matching
  `context/designs/login.png` and the build plan — not staged into two
  features.
- **Route protection = Next.js middleware checks cookie presence only**, not
  signature verification. No secret is duplicated into the frontend; the
  backend independently validates the JWT on every API call, so this is a UX
  gate, not the security boundary.
- **Nav shell ships with all 4 links now** (Dashboard/Holdings/Transactions/
  Settings), matching `context/designs/dashboard.png`. The 3 pages without a
  built feature yet get a minimal "Coming soon" placeholder.
- **Next.js owns the httpOnly cookie, not the backend.** Frontend
  (`localhost:3000`) and backend (`localhost:8000`) are different origins. A
  cookie set directly by the backend would be scoped to the backend's own
  origin — invisible to Next.js `middleware.ts` and to Server Components
  reading via `next/headers`, silently breaking the route-protection decision
  above. So:
  - Backend `/auth/*` endpoints are plain JSON — they return `{access_token}`,
    never a `Set-Cookie`.
  - Next.js Route Handlers (`app/api/auth/*`) receive that token and set the
    httpOnly cookie on the frontend's own domain.
  - Every authenticated call to the backend reads the cookie via
    `next/headers` and forwards it as `Authorization: Bearer <token>`.
  - The backend still owns 100% of the auth logic (issuing, signing,
    validating JWTs, running the Google OAuth exchange) — only *who writes
    the Set-Cookie header* moves to the frontend. Does not reopen ADR-0002.
- **Auth library = Authlib only** (covers both the Google OAuth client and
  JWT encode/decode via `authlib.jose`) — not Authlib + python-jose.
- **Password hashing = `passlib[bcrypt]`.**
- **JWT = single 7-day access token, no refresh-token rotation.** MVP,
  single-owner-first usage; re-login after 7 days is an acceptable cost.
- **`users` table + first Alembic migration is built in this feature**, not
  02, even though 02 is titled "Database schema" — login needs somewhere to
  persist a user. 02 adds the remaining tables onto the same `Base`.
- **Google OAuth flow stays same-origin on the backend, then hands off to the
  frontend via a one-time code** (necessary consequence of "Next.js owns the
  cookie" — Authlib/Starlette session-based `state` verification only works
  if `/authorize` and `/callback` land on the same origin):
  1. `GET /auth/google/login` (backend) → redirects to Google.
  2. Google → `GET /auth/google/callback` (backend) → exchanges the code,
     finds-or-creates the `User`, mints a short-lived one-time exchange code
     (in-memory dict + ~60s TTL — single-process MVP, no new table),
     redirects to `{FRONTEND_ORIGIN}/auth/callback?code=...`.
  3. `frontend/app/(auth)/callback/route.ts` (a Route Handler, not a page)
     reads `code`, calls backend `POST /auth/exchange` server-to-server, gets
     `{access_token}`, sets the httpOnly cookie, redirects to `/dashboard`.
  The raw JWT is never put in a URL or browser history — only a single-use,
  60s-lived opaque code is.
- **Backend code placement matches the `health.py` precedent**:
  `app/core/security.py` (pure: hash/verify password, create/decode JWT — no
  FastAPI, no SQLAlchemy), `app/core/oauth.py` (Authlib Google client
  registration + the exchange-code store), `app/api/deps.py`
  (`get_current_user`), `app/api/auth.py` (router — does its own simple
  SQLAlchemy queries directly, like `health.py` does, since this is simple
  CRUD, not complex business rules). **No `app/domain/auth.py`** this
  feature; `domain/` stays reserved for logic like valuation later.
  `SessionMiddleware`'s secret reuses `JWT_SECRET` — no new env var.
- **Separate `/signup` page** (not a toggle on `/login`), matching the
  "Create one" link in the mockup.
- **shadcn/ui installed/wired in this feature**: `components.json`,
  `globals.css` rewritten with the tokens from `05-ui-tokens.md` (replacing
  the stock create-next-app theme), Inter font. Primitives: `Button`,
  `Input`, `Label`, `Card`, `Separator`, `Avatar`. New deps:
  `class-variance-authority`, `clsx`, `tailwind-merge`,
  `@radix-ui/react-slot`, `@radix-ui/react-label`,
  `@radix-ui/react-separator`, `@radix-ui/react-avatar`. No `lucide-react`
  yet. The Google "G" mark is an inline brand SVG. Logout is a plain button
  next to the avatar, not a dropdown menu (skips
  `@radix-ui/react-dropdown-menu`) — matches the mockup, which shows no
  open-dropdown state.
- **Zod for validation, no new form library** — plain `useState` + a Zod
  schema for the two small forms.
- **Avatar initials**: from `name` if present (Google profile provides it),
  else the first letter of `email`. Email/password signup only collects
  email + password, so `name` is nullable on `User`.
- **CORS**: add `allow_credentials=True` to the existing `CORSMiddleware`.

## Assumptions

- Developer creates the Google Cloud OAuth client themselves and provides
  `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET`; dev authorized redirect URI is
  `http://localhost:8000/auth/google/callback`.
- Public sign-up, no invite-only gating.
- Single-process backend for MVP — the in-memory OAuth exchange-code store
  doesn't survive a restart or work across multiple instances; fine until a
  real deploy/scaling ADR exists.
- No password reset, no email verification, no refresh-token rotation /
  session revocation, no rate limiting or lockout on login attempts.

## Scope

**In scope:**
- Backend: `users` table + Alembic migration; `app/core/security.py`,
  `app/core/oauth.py`; `app/api/deps.py`; `app/api/auth.py`
  (`POST /auth/signup`, `POST /auth/login`, `GET /auth/google/login`,
  `GET /auth/google/callback`, `POST /auth/exchange`, `GET /me`);
  `app/schemas/auth.py`; new deps (`authlib`, `passlib[bcrypt]`,
  `itsdangerous`); `SessionMiddleware` + CORS `allow_credentials` in
  `app/main.py`; `.env.example` additions (`JWT_SECRET`, `GOOGLE_CLIENT_ID`,
  `GOOGLE_CLIENT_SECRET`); pytest coverage (signup, login happy/unhappy
  path, `/me` with/without a valid token).
- Frontend: shadcn/ui setup + `globals.css` tokens; `app/(auth)/login/page.tsx`,
  `app/(auth)/signup/page.tsx`, `app/(auth)/callback/route.ts`;
  `app/api/auth/{login,signup,logout}/route.ts`; `middleware.ts`;
  `app/(app)/layout.tsx` (nav shell, calls `/me`); `app/(app)/dashboard/page.tsx`
  (placeholder — real dashboard is feature 03), `app/(app)/holdings/page.tsx`,
  `app/(app)/transactions/page.tsx`, `app/(app)/settings/page.tsx`
  ("Coming soon" placeholders); `lib/auth/session.ts` (server-only
  cookie/Bearer helper, shared by every future protected page);
  `lib/api/auth.ts`; extend `lib/api/client.ts` with `apiPost`;
  `@playwright/test` installed + one e2e covering signup → protected page →
  logout → redirected-when-unauthenticated (email/password path only —
  Google OAuth verified manually).
- Context updates: `03-code-standards.md` (new approved deps),
  `01-architecture.md` (tighten Authentication section — which side sets the
  cookie), `07-ui-registry.md` (via `/imprint`), `08-progress-tracker.md`.

**Out of scope:**
- Password reset / forgot-password flow.
- Email verification.
- Refresh-token rotation / logout-everywhere / session revocation list.
- Real Dashboard/Holdings/Transactions/Settings pages (later features) — only
  placeholders here.
- Automated e2e coverage of the Google OAuth path.
- Rate limiting / account lockout on login attempts.

## How to build it

1. Backend deps: add `authlib`, `passlib[bcrypt]`, `itsdangerous` to
   `pyproject.toml`; `uv sync`.
2. `app/models/base.py` (declarative `Base`), `app/models/user.py` (`User`:
   id, email unique, password_hash nullable, google_id nullable unique, name
   nullable, created_at); wire `Base.metadata` into `alembic/env.py`;
   generate + apply the first migration.
3. `app/core/security.py` (hash/verify password, create/decode JWT, 7-day
   expiry) and `app/core/oauth.py` (Authlib Google client registration,
   in-memory exchange-code store with TTL).
4. `app/schemas/auth.py` (SignupRequest, LoginRequest, TokenResponse,
   ExchangeRequest, UserOut).
5. `app/api/deps.py` (`get_current_user`) and `app/api/auth.py` (all 6
   endpoints); register the router + `SessionMiddleware` +
   `allow_credentials=True` in `app/main.py`.
6. `.env.example` + `.env`: add `JWT_SECRET`, `GOOGLE_CLIENT_ID`,
   `GOOGLE_CLIENT_SECRET`; update `docker-compose.yml`'s backend service env.
7. Backend tests: `tests/test_auth.py` (signup, login happy/unhappy, `/me`
   with/without token) + a small `conftest.py` fixture that cleans up any
   test user by email after each test.
8. Frontend: install shadcn deps; write `globals.css` from
   `05-ui-tokens.md`; `components.json`; add `Button`, `Input`, `Label`,
   `Card`, `Separator`, `Avatar` under `components/ui/`.
9. `lib/api/client.ts`: add `apiPost`. `lib/api/auth.ts`: `login`, `signup`,
   `exchangeGoogleCode`, `getMe`. `lib/auth/session.ts`: server-only helpers
   to read the cookie and build the `Authorization` header.
10. `app/(auth)/login/page.tsx`, `app/(auth)/signup/page.tsx` (match
    `context/designs/login.png`); `app/api/auth/login/route.ts`,
    `.../signup/route.ts`, `.../logout/route.ts`; `app/(auth)/callback/route.ts`.
11. `middleware.ts`: redirect to `/login` if the session cookie is absent on
    `(app)` routes; redirect away from `/login`/`/signup` to `/dashboard` if
    already authenticated.
12. `app/(app)/layout.tsx` (nav shell calling `/me`), `app/(app)/dashboard/page.tsx`,
    `.../holdings/page.tsx`, `.../transactions/page.tsx`,
    `.../settings/page.tsx` (placeholders).
13. Install `@playwright/test`; one e2e: sign up → land on dashboard → log
    out → visiting `/dashboard` redirects to `/login`.
14. Update `03-code-standards.md` (new deps), `01-architecture.md`
    (Authentication section), `08-progress-tracker.md` (mark 01 done,
    advance to 02); run `/imprint` for the new components.
15. Verify end-to-end per "Done when" below.

## Done when

- [x] A user can sign up with email/password, is redirected to `/dashboard`,
      and the session persists across a page reload.
- [x] A user can log in with email/password.
- [x] A user can sign in with Google (manually verified 2026-09-30 against a
      real Google account, with the developer's own Google Cloud OAuth
      client). One Console-side snag along the way: an initial
      `redirect_uri_mismatch` — the authorized redirect URI registered on the
      OAuth client didn't exactly match `http://localhost:8000/auth/google/callback`
      (scheme/host/port/trailing-slash all have to match exactly). Fixed in
      the Google Cloud Console, not in code.
- [x] Visiting any `(app)` route while unauthenticated redirects to `/login`.
- [x] `/me` returns the current user; the app shell nav shows their initials.
- [x] Logging out clears the session and subsequent visits to `/dashboard`
      redirect to `/login`.
- [x] `ruff check` / `mypy` clean on backend; `eslint` / `tsc --noEmit` clean
      on frontend.
- [x] Backend pytest (`signup`, `login`, `/me`) passes — 10/10 (2 added
      during `/review` fixes: overlong/emoji password on signup and login).
- [x] Playwright e2e (signup → protected → logout → redirected) passes.

## Open questions

None — all resolved. Feature fully built, reviewed, and verified end to end,
including the real Google OAuth round trip.
