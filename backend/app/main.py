from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.core.config import settings

app = FastAPI(title="Invest Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Backs Authlib's Google OAuth state/nonce handshake (backend-origin only —
# see specs/01-auth-app-shell.md). Reuses JWT_SECRET to avoid a new env var.
app.add_middleware(SessionMiddleware, secret_key=settings.jwt_secret)

app.include_router(health_router)
app.include_router(auth_router)
