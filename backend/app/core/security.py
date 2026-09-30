import logging
from datetime import UTC, datetime
from uuid import UUID

import bcrypt
from joserfc import jwt
from joserfc.errors import JoseError
from joserfc.jwk import OctKey
from joserfc.jwt import JWTClaimsRegistry

from app.core.config import settings

logger = logging.getLogger(__name__)

_JWT_ALG = "HS256"
_JWT_KEY = OctKey.import_key(settings.jwt_secret)
ACCESS_TOKEN_EXPIRE_DAYS = 7

# bcrypt's hard limit is 72 *bytes*, not characters — a password well under
# any character-count limit can still exceed this with multi-byte UTF-8
# (emoji, non-Latin scripts). schemas/auth.py enforces this at the request
# boundary; these guards are defense-in-depth so this module never crashes
# regardless of caller.
_MAX_PASSWORD_BYTES = 72
# A hash of an unreachable password, used so a login for a nonexistent email
# still pays the cost of one bcrypt comparison — otherwise the early return
# below would make nonexistent-email logins measurably faster than
# wrong-password ones, leaking which emails are registered via timing.
_DUMMY_HASH = bcrypt.hashpw(b"", bcrypt.gensalt()).decode("utf-8")


def hash_password(password: str) -> str:
    encoded = password.encode("utf-8")
    if len(encoded) > _MAX_PASSWORD_BYTES:
        raise ValueError(f"Password must be at most {_MAX_PASSWORD_BYTES} bytes")
    return bcrypt.hashpw(encoded, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str | None) -> bool:
    encoded = password.encode("utf-8")
    if len(encoded) > _MAX_PASSWORD_BYTES:
        return False
    return bcrypt.checkpw(encoded, (password_hash or _DUMMY_HASH).encode("utf-8"))


def create_access_token(user_id: UUID) -> str:
    now = int(datetime.now(UTC).timestamp())
    claims = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + ACCESS_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    }
    return jwt.encode({"alg": _JWT_ALG}, claims, _JWT_KEY)


def decode_access_token(token: str) -> UUID | None:
    try:
        decoded = jwt.decode(token, _JWT_KEY, algorithms=[_JWT_ALG])
        JWTClaimsRegistry().validate(decoded.claims)
    except JoseError:
        logger.warning("[security.decode_access_token] invalid or expired token")
        return None

    sub = decoded.claims.get("sub")
    if not isinstance(sub, str):
        return None
    try:
        return UUID(sub)
    except ValueError:
        logger.warning("[security.decode_access_token] token 'sub' is not a valid UUID")
        return None
