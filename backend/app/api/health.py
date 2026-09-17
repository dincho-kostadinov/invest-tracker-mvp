import logging

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.db import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
def get_health(response: Response, db: Session = Depends(get_db)) -> dict[str, str]:
    # Intentionally not delegated to app/domain: the domain layer must stay
    # framework-free (no SQLAlchemy imports), and this is an infra probe,
    # not a business rule.
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        logger.exception("[health.get_health] database check failed")
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "error", "database": "unreachable"}
    return {"status": "ok", "database": "connected"}
