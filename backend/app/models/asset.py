import uuid
from datetime import datetime

from sqlalchemy import CHAR, DateTime, ForeignKey, Index, String, UniqueConstraint, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.base import Base
from app.models.enums import AssetKind, AssetUnit, enum_check


class Asset(Base):
    """An instrument one user defined (fund, gold, stock). Per-user (ADR-0004)."""

    __tablename__ = "assets"
    __table_args__ = (
        # Target of composite FKs from holdings (ADR-0004).
        UniqueConstraint("id", "user_id", name="uq_assets_id_user_id"),
        Index(
            "uq_assets_user_id_isin",
            "user_id",
            "isin",
            unique=True,
            postgresql_where=text("isin IS NOT NULL"),
        ),
        enum_check("kind", AssetKind, "ck_assets_kind"),
        enum_check("unit", AssetUnit, "ck_assets_unit"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    kind: Mapped[str] = mapped_column(String(10))
    name: Mapped[str] = mapped_column(String(200))
    isin: Mapped[str | None] = mapped_column(String(12))
    symbol: Mapped[str | None] = mapped_column(String(20))
    currency: Mapped[str] = mapped_column(CHAR(3))
    unit: Mapped[str] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
