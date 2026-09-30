from collections.abc import Generator

import pytest

from app.core.db import SessionLocal
from app.models import User


@pytest.fixture
def cleanup_user() -> Generator[list[str], None, None]:
    """Collects emails created during a test and deletes them afterward."""
    emails: list[str] = []
    yield emails
    if not emails:
        return
    db = SessionLocal()
    try:
        db.query(User).filter(User.email.in_(emails)).delete(synchronize_session=False)
        db.commit()
    finally:
        db.close()
