import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import CHAR, Date, DateTime, ForeignKey, Numeric, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.base import Base


class PriceSnapshot(Base):
    """One unit price per asset per day. Per-user via its asset (ADR-0004)."""

    __tablename__ = "price_snapshots"
    __table_args__ = (
        UniqueConstraint("asset_id", "as_of", name="uq_price_snapshots_asset_id_as_of"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    asset_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("assets.id", ondelete="CASCADE"))
    as_of: Mapped[date] = mapped_column(Date)
    price: Mapped[Decimal] = mapped_column(Numeric(20, 6))
    currency: Mapped[str] = mapped_column(CHAR(3))
    source: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
