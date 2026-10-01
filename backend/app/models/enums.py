from enum import StrEnum

from sqlalchemy import CheckConstraint


class AccountType(StrEnum):
    FUND_PLATFORM = "fund_platform"
    BROKER = "broker"
    PHYSICAL = "physical"


class AssetKind(StrEnum):
    FUND = "FUND"
    GOLD = "GOLD"
    STOCK = "STOCK"


class AssetUnit(StrEnum):
    SHARE = "share"
    GRAM = "gram"


class TransactionType(StrEnum):
    BUY = "BUY"
    SELL = "SELL"
    DIVIDEND = "DIVIDEND"
    FEE = "FEE"


def enum_check(column: str, enum: type[StrEnum], name: str) -> CheckConstraint:
    """CHECK constraint limiting a VARCHAR column to the enum's values (not a native ENUM)."""
    values = ", ".join(f"'{member.value}'" for member in enum)
    return CheckConstraint(f"{column} IN ({values})", name=name)
