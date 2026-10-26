import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime, Enum, ForeignKey, types
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy.orm import relationship
from ulid import ULID
from app.database import Base

def generate_ulid() -> str:
    return str(ULID())

class AccountType(str, enum.Enum):
    BANK = "bank"
    CREDIT_CARD = "credit_card"
    INVESTMENT = "investment"

class SafeAccountType(types.TypeDecorator):
    """Resilient AccountType Enum decorator supporting case-insensitive DB values across PostgreSQL and SQLite."""
    impl = types.String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(
                PG_ENUM(
                    "BANK", "CREDIT_CARD", "INVESTMENT", "bank", "credit_card", "investment",
                    name="accounttype",
                    create_type=False
                )
            )
        return dialect.type_descriptor(types.String())

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, AccountType):
            return value.name
        val_str = str(value).upper()
        if val_str in AccountType.__members__:
            return val_str
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        val_str = str(value).upper()
        if val_str in AccountType.__members__:
            return AccountType[val_str]
        try:
            return AccountType(str(value).lower())
        except ValueError:
            return AccountType.BANK

class AssetClass(str, enum.Enum):
    MUTUAL_FUNDS = "mutualFunds"
    GOLD = "gold"
    STOCKS = "stocks"
    BONDS = "bonds"
    CRYPTO = "crypto"
    OTHER = "other"

class TransactionType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")

class Account(Base):
    __tablename__ = "accounts"

    id = Column(String(26), primary_key=True, index=True, default=generate_ulid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    name = Column(String(100), nullable=False)
    account_type = Column(SafeAccountType, nullable=False, default=AccountType.BANK)
    balance = Column(Float, nullable=False, default=0.0)
    include_in_net_worth = Column(Boolean, nullable=False, default=True)
    asset_class = Column(String(50), nullable=True, default=None)
    currency = Column(String(10), nullable=False, default="INR")
    notes = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan", foreign_keys="[Transaction.account_id]")

class Category(Base):
    __tablename__ = "categories"

    id = Column(String(26), primary_key=True, index=True, default=generate_ulid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    name = Column(String(50), nullable=False, index=True)
    category_type = Column(Enum(TransactionType), nullable=False, index=True)
    icon = Column(String(50), nullable=True)
    is_default = Column(Boolean, nullable=False, default=False)
    # parent_id enables super-category hierarchy (e.g. Shopping → Clothing, Beauty).
    # NULL means this is a top-level or standalone category.
    parent_id = Column(String(26), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(26), primary_key=True, index=True, default=generate_ulid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    account_id = Column(String(26), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    transaction_type = Column(Enum(TransactionType), nullable=False, default=TransactionType.EXPENSE)
    amount = Column(Float, nullable=False)
    category = Column(String(50), nullable=False, default="other", index=True)
    description = Column(String(255), nullable=True)
    is_transfer = Column(Boolean, nullable=False, default=False)
    transfer_destination_account_id = Column(String(26), ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True, index=True)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User", back_populates="transactions")
    account = relationship("Account", back_populates="transactions", foreign_keys=[account_id])
