import json
import uuid
from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.models import Account, Asset, Holding, Transaction, User
from app.schemas.auth import LoginRequest
from app.seed import (
    BACKEND_DIR,
    DEMO_EMAIL,
    EXAMPLE_DATA_FILE,
    REAL_DATA_FILE,
    load_seed_data,
    resolve_seed_path,
    seed,
)

EXAMPLE = BACKEND_DIR / EXAMPLE_DATA_FILE
PASSWORD = "demo-password-for-tests"


def _email(cleanup_user: list[str]) -> str:
    email = f"test-seed-{uuid.uuid4().hex}@example.com"
    cleanup_user.append(email)
    return email


def _count(db: Session, model: type[Account | Asset | Holding | Transaction], user: User) -> int:
    return db.scalar(select(func.count()).select_from(model).where(model.user_id == user.id)) or 0


def test_seed_creates_demo_portfolio(db: Session, cleanup_user: list[str]) -> None:
    email = _email(cleanup_user)

    assert seed(db, load_seed_data(EXAMPLE), PASSWORD, email=email) is True

    user = db.scalars(select(User).where(User.email == email)).one()
    assert verify_password(PASSWORD, user.password_hash)
    assert _count(db, Account, user) == 3
    assert _count(db, Asset, user) == 4
    assert _count(db, Holding, user) == 4
    assert _count(db, Transaction, user) == 7

    gold = db.scalars(select(Asset).where(Asset.user_id == user.id, Asset.kind == "GOLD")).one()
    gold_holding = db.scalars(select(Holding).where(Holding.asset_id == gold.id)).one()
    assert gold_holding.quantity == Decimal("7.5")
    assert gold_holding.cost_basis_minor == 80000
    buys = db.scalars(select(Transaction).where(Transaction.holding_id == gold_holding.id)).all()
    assert sum(t.amount_minor for t in buys) == gold_holding.cost_basis_minor
    assert all(t.type == "BUY" for t in buys)


def test_seed_is_idempotent(db: Session, cleanup_user: list[str]) -> None:
    email = _email(cleanup_user)
    data = load_seed_data(EXAMPLE)
    seed(db, data, PASSWORD, email=email)

    assert seed(db, data, PASSWORD, email=email) is False

    user = db.scalars(select(User).where(User.email == email)).one()
    assert _count(db, Holding, user) == 4
    assert _count(db, Transaction, user) == 7


def test_seed_rejects_buys_that_dont_match_holding(tmp_path: Path) -> None:
    raw = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    raw["holdings"][0]["cost_basis"] = "999.99"  # BUY amounts sum to 1000.00
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(raw), encoding="utf-8")

    with pytest.raises(ValidationError):
        load_seed_data(bad)


def test_seed_path_falls_back_to_example(tmp_path: Path) -> None:
    (tmp_path / EXAMPLE_DATA_FILE).write_text("{}", encoding="utf-8")
    assert resolve_seed_path(tmp_path).name == EXAMPLE_DATA_FILE

    (tmp_path / REAL_DATA_FILE).write_text("{}", encoding="utf-8")
    assert resolve_seed_path(tmp_path).name == REAL_DATA_FILE


def test_real_seed_file_is_valid_when_present() -> None:
    real = BACKEND_DIR / REAL_DATA_FILE
    if not real.exists():
        pytest.skip("no local seed_data.json")
    data = load_seed_data(real)
    assert len(data.holdings) == 4


def test_demo_email_passes_login_validation() -> None:
    # email-validator rejects special-use domains like .local/.test - the demo user
    # must be able to log in through the real auth endpoint.
    LoginRequest(email=DEMO_EMAIL, password="irrelevant")
