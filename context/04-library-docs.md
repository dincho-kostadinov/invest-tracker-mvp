# Library Docs

Project-specific usage rules. Stack per ADR-0002 (FastAPI backend + Next.js frontend).

## Before Using Any Library (universal)

1. Check `AGENTS.md` / `.claude/skills/` for an installed skill.
2. Check for a configured MCP server; prefer it for live docs.
3. Read this file for project-specific patterns.

Order of authority: MCP docs → installed skill → this file → training knowledge.

## Backend

### FastAPI
- Routers thin; inject dependencies (DB session, current user) via `Depends`.
- Request/response models are Pydantic; never return ORM objects directly.
- The OpenAPI schema is the contract — the frontend client is generated from it.

### SQLAlchemy + Alembic
- Models in `backend/app/models`; every migration via Alembic (no manual schema edits).
- Money columns are integers (minor units) with a sibling currency column.
- Every user-data query filters by `user_id`. No unscoped queries.

### Pydantic / pydantic-settings
- Validate every external payload (market data) and every request at the boundary.
- All config loaded from env via `pydantic-settings`.

### Auth (Authlib / JWT + passlib)
- Backend issues JWTs; Google OAuth + email/password (passwords hashed with passlib).
- Current user resolved from the token in a `Depends`; the domain layer receives `user_id`, never the request.

### httpx (market data / connectors)
- All outbound calls use `httpx` inside `marketdata` / `connectors`, behind the provider interface (ADR-0001). Cache; wrap in try/except; fall back to last snapshot or manual price.

### APScheduler
- The daily valuation job lives in `backend/app/jobs`; must also be manually triggerable (endpoint or CLI) for testing.

## Frontend

### Typed API client (`frontend/lib/api`)
- Generated from FastAPI's OpenAPI schema. Components call the client, never raw `fetch`.

### Recharts
- Charts in `components/`, fed already-computed data from the API — no return math on the frontend.

### Zod
- Validate form input before calling the API.
