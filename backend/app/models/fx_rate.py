import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import CHAR, Date, DateTime, Numeric, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.base import Base


class FxRate(Base):
    """One rate per currency pair per day: 1 `base` = `rate` `quote`. Global, not per-user."""

    __tablename__ = "fx_rates"
    __table_args__ = (
        UniqueConstraint("as_of", "base", "quote", name="uq_fx_rates_as_of_base_quote"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    as_of: Mapped[date] = mapped_column(Date)
    base: Mapped[str] = mapped_column(CHAR(3))
    quote: Mapped[str] = mapped_column(CHAR(3))
    rate: Mapped[Decimal] = mapped_column(Numeric(20, 8))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
