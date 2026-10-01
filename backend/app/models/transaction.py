import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CHAR,
    BigInteger,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Numeric,
    String,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.base import Base
from app.models.enums import TransactionType, enum_check


class Transaction(Base):
    """A buy/sell/dividend/fee against a holding.

    `quantity` and `price` are null for DIVIDEND/FEE; `amount_minor` is the exact
    cash moved (ADR-0003).
    """

    __tablename__ = "transactions"
    __table_args__ = (
        # Composite FK: the holding must belong to the same user (ADR-0004).
        ForeignKeyConstraint(
            ["holding_id", "user_id"],
            ["holdings.id", "holdings.user_id"],
            ondelete="CASCADE",
            name="fk_transactions_holding_id_user_id_holdings",
        ),
        enum_check("type", TransactionType, "ck_transactions_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    holding_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)
    type: Mapped[str] = mapped_column(String(10))
    quantity: Mapped[Decimal | None] = mapped_column(Numeric(20, 8))
    price: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    amount_minor: Mapped[int] = mapped_column(BigInteger)
    fee_minor: Mapped[int] = mapped_column(BigInteger, server_default="0")
    currency: Mapped[str] = mapped_column(CHAR(3))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
