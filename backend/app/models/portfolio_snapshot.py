import uuid
from datetime import date, datetime

from sqlalchemy import CHAR, BigInteger, Date, DateTime, ForeignKey, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.base import Base


class PortfolioSnapshot(Base):
    """A user's total portfolio value for one day, in their base currency."""

    __tablename__ = "portfolio_snapshots"
    __table_args__ = (
        UniqueConstraint("user_id", "as_of", name="uq_portfolio_snapshots_user_id_as_of"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"))
    as_of: Mapped[date] = mapped_column(Date)
    total_value_minor: Mapped[int] = mapped_column(BigInteger)
    base_currency: Mapped[str] = mapped_column(CHAR(3))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
