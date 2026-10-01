import uuid
from collections.abc import Callable
from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.models import (
    Account,
    Asset,
    Holding,
    PortfolioSnapshot,
    PriceSnapshot,
    Transaction,
    User,
)


def _account(db: Session, user: User) -> Account:
    account = Account(user_id=user.id, name=f"acc-{uuid.uuid4().hex[:8]}", type="fund_platform")
    db.add(account)
    db.flush()
    return account


def _asset(db: Session, user: User, isin: str | None = None) -> Asset:
    asset = Asset(
        user_id=user.id, kind="FUND", name="Fund", isin=isin, currency="EUR", unit="share"
    )
    db.add(asset)
    db.flush()
    return asset


def _holding(db: Session, user: User, account: Account, asset: Asset) -> Holding:
    holding = Holding(
        user_id=user.id,
        account_id=account.id,
        asset_id=asset.id,
        quantity=Decimal("1"),
        cost_basis_minor=100,
        currency="EUR",
    )
    db.add(holding)
    db.flush()
    return holding


def _buy(db: Session, user_id: uuid.UUID, holding: Holding) -> Transaction:
    tx = Transaction(
        user_id=user_id,
        holding_id=holding.id,
        type="BUY",
        quantity=Decimal("1"),
        price=Decimal("1"),
        amount_minor=100,
        currency="EUR",
        occurred_at=datetime.now(UTC),
    )
    db.add(tx)
    db.flush()
    return tx


def test_holding_rejects_other_users_account(db: Session, make_user: Callable[[], User]) -> None:
    alice, bob = make_user(), make_user()
    bobs_account = _account(db, bob)
    alices_asset = _asset(db, alice)

    with pytest.raises(IntegrityError):
        _holding(db, alice, bobs_account, alices_asset)


def test_holding_rejects_other_users_asset(db: Session, make_user: Callable[[], User]) -> None:
    alice, bob = make_user(), make_user()
    alices_account = _account(db, alice)
    bobs_asset = _asset(db, bob)

    with pytest.raises(IntegrityError):
        _holding(db, alice, alices_account, bobs_asset)


def test_transaction_rejects_other_users_holding(
    db: Session, make_user: Callable[[], User]
) -> None:
    alice, bob = make_user(), make_user()
    holding = _holding(db, alice, _account(db, alice), _asset(db, alice))

    with pytest.raises(IntegrityError):
        _buy(db, bob.id, holding)


def test_deleting_user_cascades_everything(db: Session, make_user: Callable[[], User]) -> None:
    user = make_user()
    account, asset = _account(db, user), _asset(db, user)
    holding = _holding(db, user, account, asset)
    _buy(db, user.id, holding)
    db.add(
        PriceSnapshot(
            asset_id=asset.id,
            as_of=date.today(),
            price=Decimal("1"),
            currency="EUR",
            source="manual",
        )
    )
    db.add(
        PortfolioSnapshot(
            user_id=user.id, as_of=date.today(), total_value_minor=100, base_currency="EUR"
        )
    )
    db.commit()
    asset_id = asset.id

    db.execute(text("DELETE FROM users WHERE id = :id"), {"id": user.id})
    db.commit()

    for model in (Account, Asset, Holding, Transaction, PortfolioSnapshot):
        assert db.scalars(select(model).where(model.user_id == user.id)).first() is None
    assert (
        db.scalars(select(PriceSnapshot).where(PriceSnapshot.asset_id == asset_id)).first() is None
    )


@pytest.mark.parametrize("table", ["accounts", "assets"])
def test_deleting_account_or_asset_with_holdings_is_refused(
    db: Session, make_user: Callable[[], User], table: str
) -> None:
    user = make_user()
    account, asset = _account(db, user), _asset(db, user)
    _holding(db, user, account, asset)
    db.commit()
    target_id = account.id if table == "accounts" else asset.id

    with pytest.raises(IntegrityError):
        db.execute(text(f"DELETE FROM {table} WHERE id = :id"), {"id": target_id})


def test_deleting_asset_cascades_its_price_snapshots(
    db: Session, make_user: Callable[[], User]
) -> None:
    user = make_user()
    asset = _asset(db, user)
    db.add(
        PriceSnapshot(
            asset_id=asset.id,
            as_of=date.today(),
            price=Decimal("1"),
            currency="EUR",
            source="manual",
        )
    )
    db.commit()
    asset_id = asset.id

    db.execute(text("DELETE FROM assets WHERE id = :id"), {"id": asset_id})
    db.commit()

    assert (
        db.scalars(select(PriceSnapshot).where(PriceSnapshot.asset_id == asset_id)).first() is None
    )


def test_deleting_holding_cascades_its_transactions(
    db: Session, make_user: Callable[[], User]
) -> None:
    user = make_user()
    holding = _holding(db, user, _account(db, user), _asset(db, user))
    _buy(db, user.id, holding)
    db.commit()
    holding_id = holding.id

    db.execute(text("DELETE FROM holdings WHERE id = :id"), {"id": holding_id})
    db.commit()

    assert (
        db.scalars(select(Transaction).where(Transaction.holding_id == holding_id)).first() is None
    )


@pytest.mark.parametrize(
    ("model", "field", "value"),
    [
        ("account", "type", "bank"),
        ("asset", "kind", "CRYPTO"),
        ("asset", "unit", "ounce"),
        ("transaction", "type", "TRANSFER"),
    ],
)
def test_values_outside_allowed_enums_are_rejected(
    db: Session, make_user: Callable[[], User], model: str, field: str, value: str
) -> None:
    user = make_user()
    with pytest.raises(IntegrityError):
        if model == "account":
            db.add(Account(user_id=user.id, name="x", type=value))
        elif model == "asset":
            fields = {"kind": "FUND", "unit": "share", field: value}
            db.add(Asset(user_id=user.id, name="x", currency="EUR", **fields))
        else:
            holding = _holding(db, user, _account(db, user), _asset(db, user))
            db.add(
                Transaction(
                    user_id=user.id,
                    holding_id=holding.id,
                    type=value,
                    amount_minor=100,
                    currency="EUR",
                    occurred_at=datetime.now(UTC),
                )
            )
        db.flush()


def test_isin_is_unique_per_user_not_globally(db: Session, make_user: Callable[[], User]) -> None:
    alice, bob = make_user(), make_user()
    isin = "LU" + uuid.uuid4().hex[:10].upper()
    _asset(db, alice, isin)
    _asset(db, bob, isin)  # a different user may hold the same ISIN
    db.commit()

    with pytest.raises(IntegrityError):
        _asset(db, alice, isin)


def test_assets_without_isin_are_not_unique_constrained(
    db: Session, make_user: Callable[[], User]
) -> None:
    user = make_user()
    _asset(db, user, None)
    _asset(db, user, None)  # e.g. two gold assets — no ISIN, no conflict
    db.commit()


def test_numeric_values_round_trip_exactly(make_user: Callable[[], User]) -> None:
    user = make_user()
    write = SessionLocal()
    try:
        holding = _holding(write, user, _account(write, user), _asset(write, user))
        holding.quantity = Decimal("181.905")
        tx = _buy(write, user.id, holding)
        tx.price = Decimal("27.593237")
        write.commit()
        holding_id, tx_id = holding.id, tx.id
    finally:
        write.close()

    read = SessionLocal()
    try:
        stored_holding = read.get(Holding, holding_id)
        stored_tx = read.get(Transaction, tx_id)
        assert stored_holding is not None and stored_tx is not None
        assert isinstance(stored_holding.quantity, Decimal)
        assert stored_holding.quantity == Decimal("181.905")
        assert stored_tx.price == Decimal("27.593237")
    finally:
        read.close()
