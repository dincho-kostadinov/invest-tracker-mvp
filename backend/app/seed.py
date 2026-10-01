"""Seed the demo user and their portfolio.

Run manually: `uv run python -m app.seed`. Idempotent — if the demo user already
exists, nothing is changed. Reads the real positions from the gitignored
`backend/seed_data.json`, falling back to the committed `seed_data.example.json`.
"""

import json
import logging
import sys
from datetime import UTC, date, datetime, time
from decimal import ROUND_HALF_EVEN, Decimal
from pathlib import Path
from typing import Self

from pydantic import BaseModel, Field, model_validator
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import SessionLocal
from app.core.security import hash_password
from app.models import Account, Asset, Holding, Transaction, User
from app.models.enums import AccountType, AssetKind, AssetUnit, TransactionType

logger = logging.getLogger(__name__)

DEMO_EMAIL = "demo@investtracker.example"
DEMO_NAME = "Demo User"
BACKEND_DIR = Path(__file__).resolve().parent.parent
REAL_DATA_FILE = "seed_data.json"
EXAMPLE_DATA_FILE = "seed_data.example.json"

_CENT = Decimal("0.01")
_PRICE_SCALE = Decimal("0.000001")


class SeedBuy(BaseModel):
    occurred_at: date
    quantity: Decimal = Field(gt=0)
    amount: Decimal = Field(gt=0)  # major units, e.g. "5019.14"


class SeedAsset(BaseModel):
    kind: AssetKind
    name: str
    isin: str | None = None
    symbol: str | None = None
    currency: str = Field(min_length=3, max_length=3)
    unit: AssetUnit


class SeedHolding(BaseModel):
    account: str  # SeedAccount.name
    asset: SeedAsset
    quantity: Decimal = Field(gt=0)
    cost_basis: Decimal = Field(gt=0)  # major units
    buys: list[SeedBuy] = Field(min_length=1)

    @model_validator(mode="after")
    def buys_match_totals(self) -> Self:
        if sum(b.quantity for b in self.buys) != self.quantity:
            raise ValueError(f"{self.asset.name}: BUY quantities don't sum to {self.quantity}")
        if sum(b.amount for b in self.buys) != self.cost_basis:
            raise ValueError(f"{self.asset.name}: BUY amounts don't sum to {self.cost_basis}")
        return self


class SeedAccount(BaseModel):
    name: str
    type: AccountType


class SeedData(BaseModel):
    accounts: list[SeedAccount]
    holdings: list[SeedHolding]

    @model_validator(mode="after")
    def holdings_reference_known_accounts(self) -> Self:
        names = {a.name for a in self.accounts}
        for h in self.holdings:
            if h.account not in names:
                raise ValueError(f"{h.asset.name}: unknown account '{h.account}'")
        return self


def to_minor(amount: Decimal) -> int:
    """Major units → integer minor units. Refuses sub-cent values rather than rounding."""
    if amount != amount.quantize(_CENT):
        raise ValueError(f"Amount {amount} has more than 2 decimal places")
    return int(amount * 100)


def resolve_seed_path(directory: Path = BACKEND_DIR) -> Path:
    real = directory / REAL_DATA_FILE
    return real if real.exists() else directory / EXAMPLE_DATA_FILE


def load_seed_data(path: Path) -> SeedData:
    return SeedData.model_validate(json.loads(path.read_text(encoding="utf-8")))


def seed(db: Session, data: SeedData, password: str, email: str = DEMO_EMAIL) -> bool:
    """Create the demo user and portfolio in one DB transaction.

    Returns False (and changes nothing) if a user with `email` already exists.
    """
    if db.query(User).filter(User.email == email).first() is not None:
        return False

    # Convert every amount up front so bad data fails before anything is written.
    cost_basis = [to_minor(h.cost_basis) for h in data.holdings]
    buy_amounts = [[to_minor(b.amount) for b in h.buys] for h in data.holdings]

    user = User(email=email, name=DEMO_NAME, password_hash=hash_password(password))
    db.add(user)
    db.flush()

    accounts: dict[str, Account] = {}
    for a in data.accounts:
        accounts[a.name] = Account(user_id=user.id, name=a.name, type=a.type.value)
        db.add(accounts[a.name])
    db.flush()

    for h, basis_minor, amounts in zip(data.holdings, cost_basis, buy_amounts, strict=True):
        asset = Asset(
            user_id=user.id,
            kind=h.asset.kind.value,
            name=h.asset.name,
            isin=h.asset.isin,
            symbol=h.asset.symbol,
            currency=h.asset.currency,
            unit=h.asset.unit.value,
        )
        db.add(asset)
        db.flush()

        holding = Holding(
            user_id=user.id,
            account_id=accounts[h.account].id,
            asset_id=asset.id,
            quantity=h.quantity,
            cost_basis_minor=basis_minor,
            currency=h.asset.currency,
        )
        db.add(holding)
        db.flush()

        for buy, amount_minor in zip(h.buys, amounts, strict=True):
            db.add(
                Transaction(
                    user_id=user.id,
                    holding_id=holding.id,
                    type=TransactionType.BUY.value,
                    quantity=buy.quantity,
                    price=(buy.amount / buy.quantity).quantize(
                        _PRICE_SCALE, rounding=ROUND_HALF_EVEN
                    ),
                    amount_minor=amount_minor,
                    fee_minor=0,
                    currency=h.asset.currency,
                    occurred_at=datetime.combine(buy.occurred_at, time.min, tzinfo=UTC),
                )
            )

    db.commit()
    return True


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    if not settings.seed_demo_password:
        logger.error("[seed.main] SEED_DEMO_PASSWORD is not set in backend/.env")
        return 1

    path = resolve_seed_path()
    logger.info("[seed.main] Using %s", path.name)
    data = load_seed_data(path)

    db = SessionLocal()
    try:
        created = seed(db, data, settings.seed_demo_password)
    except Exception:
        db.rollback()
        logger.exception("[seed.main] Seeding failed; no changes were made")
        return 1
    finally:
        db.close()

    if created:
        logger.info("[seed.main] Created %s with %d holdings", DEMO_EMAIL, len(data.holdings))
    else:
        logger.info("[seed.main] %s already exists; nothing to do", DEMO_EMAIL)
    return 0


if __name__ == "__main__":
    sys.exit(main())
