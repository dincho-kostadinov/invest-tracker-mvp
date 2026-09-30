import logging
import secrets
import time
import uuid

from authlib.integrations.starlette_client import OAuth

from app.core.config import settings

logger = logging.getLogger(__name__)

oauth = OAuth()
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    client_kwargs={"scope": "openid email profile"},
)

GOOGLE_REDIRECT_URI = f"{settings.backend_origin}/auth/google/callback"

# One-time exchange codes bridging the Google callback (backend origin) to the
# frontend's cookie-setting Route Handler (see specs/01-auth-app-shell.md).
# In-memory only: fine for a single-process MVP, not for multiple instances.
_EXCHANGE_CODE_TTL_SECONDS = 60
_pending_exchanges: dict[str, tuple[uuid.UUID, float]] = {}


def _sweep_expired_exchanges() -> None:
    now = time.monotonic()
    expired = [code for code, (_, expires_at) in _pending_exchanges.items() if now > expires_at]
    for code in expired:
        del _pending_exchanges[code]


def create_exchange_code(user_id: uuid.UUID) -> str:
    # An abandoned Google flow (tab closed mid-redirect) never calls
    # consume_exchange_code, so sweep expired entries here too — otherwise
    # they'd sit in memory for the life of the process.
    _sweep_expired_exchanges()
    code = secrets.token_urlsafe(32)
    _pending_exchanges[code] = (user_id, time.monotonic() + _EXCHANGE_CODE_TTL_SECONDS)
    return code


def consume_exchange_code(code: str) -> uuid.UUID | None:
    entry = _pending_exchanges.pop(code, None)
    if entry is None:
        return None
    user_id, expires_at = entry
    if time.monotonic() > expires_at:
        logger.warning("[oauth.consume_exchange_code] exchange code expired")
        return None
    return user_id
