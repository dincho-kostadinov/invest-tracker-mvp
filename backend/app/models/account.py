import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.base import Base
from app.models.enums import AccountType, enum_check


class Account(Base):
    """A platform or place where a user keeps assets (e.g. "Amundi", "Home safe")."""

    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_accounts_user_id_name"),
        # Target of composite FKs from holdings (ADR-0004).
        UniqueConstraint("id", "user_id", name="uq_accounts_id_user_id"),
        enum_check("type", AccountType, "ck_accounts_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(100))
    type: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
