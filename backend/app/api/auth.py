import logging

from authlib.integrations.base_client.errors import OAuthError
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.db import get_db
from app.core.oauth import (
    GOOGLE_REDIRECT_URI,
    consume_exchange_code,
    create_exchange_code,
    oauth,
)
from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.schemas.auth import (
    ExchangeRequest,
    LoginRequest,
    SignupRequest,
    TokenResponse,
    UserOut,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["auth"])


@router.post("/auth/signup", response_model=TokenResponse)
def signup(body: SignupRequest, db: Session = Depends(get_db)) -> TokenResponse:
    existing = db.scalar(select(User).where(User.email == body.email))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email is already registered"
        )

    user = User(email=body.email, password_hash=hash_password(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenResponse(access_token=create_access_token(user.id))


@router.post("/auth/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == body.email))
    # Always run the bcrypt comparison, even for a nonexistent email — an
    # early return here would make a nonexistent-email login measurably
    # faster than a wrong-password one, leaking which emails are registered.
    password_hash = user.password_hash if user is not None else None
    password_ok = verify_password(body.password, password_hash)
    if user is None or not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
    return TokenResponse(access_token=create_access_token(user.id))


@router.get("/auth/google/login")
async def google_login(request: Request) -> RedirectResponse:
    redirect: RedirectResponse = await oauth.google.authorize_redirect(
        request, GOOGLE_REDIRECT_URI
    )
    return redirect


@router.get("/auth/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)) -> RedirectResponse:
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        logger.exception("[auth.google_callback] Google token exchange failed")
        return RedirectResponse(f"{settings.frontend_origin}/login?error=google_oauth_failed")

    userinfo = token.get("userinfo") or {}
    google_id = userinfo.get("sub")
    email = userinfo.get("email")
    email_verified = userinfo.get("email_verified", False)
    if not google_id or not email or not email_verified:
        logger.error(
            "[auth.google_callback] Google userinfo missing sub/email or email unverified"
        )
        return RedirectResponse(f"{settings.frontend_origin}/login?error=google_oauth_failed")

    user = db.scalar(select(User).where(User.google_id == google_id))
    if user is None:
        # Only link to an existing email/password account by email when
        # Google has itself verified that email — otherwise this becomes an
        # account-takeover path (attach a Google identity to someone else's
        # local account by matching an unverified email address).
        user = db.scalar(select(User).where(User.email == email))
    if user is None:
        user = User(email=email, google_id=google_id, name=userinfo.get("name"))
        db.add(user)
    else:
        user.google_id = google_id
        if user.name is None:
            user.name = userinfo.get("name")
    db.commit()
    db.refresh(user)

    code = create_exchange_code(user.id)
    return RedirectResponse(f"{settings.frontend_origin}/auth/callback?code={code}")


@router.post("/auth/exchange", response_model=TokenResponse)
def exchange(body: ExchangeRequest) -> TokenResponse:
    user_id = consume_exchange_code(body.code)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired code"
        )
    return TokenResponse(access_token=create_access_token(user_id))


@router.get("/me", response_model=UserOut)
def get_me(user: User = Depends(get_current_user)) -> UserOut:
    return UserOut(id=user.id, email=user.email, name=user.name)
