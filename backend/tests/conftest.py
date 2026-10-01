import uuid
from collections.abc import Callable, Generator

import pytest
from sqlalchemy.orm import Session

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


@pytest.fixture
def db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def make_user(cleanup_user: list[str]) -> Callable[[], User]:
    """Creates committed users with unique emails; deleted (with cascades) afterward."""

    def _make() -> User:
        email = f"test-{uuid.uuid4().hex}@example.com"
        cleanup_user.append(email)
        db = SessionLocal()
        try:
            user = User(email=email)
            db.add(user)
            db.commit()
            db.refresh(user)
            db.expunge(user)
            return user
        finally:
            db.close()

    return _make
