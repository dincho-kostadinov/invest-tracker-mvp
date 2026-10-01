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
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.base import Base


class Holding(Base):
    """One user's position in one asset at one account.

    Stores the total cost basis, not a per-unit average (ADR-0003).
    """

    __tablename__ = "holdings"
    __table_args__ = (
        UniqueConstraint("account_id", "asset_id", name="uq_holdings_account_id_asset_id"),
        # Target of the composite FK from transactions (ADR-0004).
        UniqueConstraint("id", "user_id", name="uq_holdings_id_user_id"),
        # Composite FKs: the account and asset must belong to the same user (ADR-0004).
        # NO ACTION (not RESTRICT) so a user delete can cascade through both sides in
        # one statement; a standalone account/asset delete is still refused.
        ForeignKeyConstraint(
            ["account_id", "user_id"],
            ["accounts.id", "accounts.user_id"],
            name="fk_holdings_account_id_user_id_accounts",
        ),
        ForeignKeyConstraint(
            ["asset_id", "user_id"],
            ["assets.id", "assets.user_id"],
            name="fk_holdings_asset_id_user_id_assets",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    account_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)
    asset_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 8))
    cost_basis_minor: Mapped[int] = mapped_column(BigInteger)
    currency: Mapped[str] = mapped_column(CHAR(3))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
