import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class AccountType(str, enum.Enum):
    BANK = "bank"
    CREDIT_CARD = "credit_card"

class TransactionType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    account_type = Column(Enum(AccountType), nullable=False, default=AccountType.BANK)
    balance = Column(Float, nullable=False, default=0.0)
    include_in_net_worth = Column(Boolean, nullable=False, default=True)
    currency = Column(String(10), nullable=False, default="INR")
    notes = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False, index=True)
    category_type = Column(Enum(TransactionType), nullable=False, index=True)
    icon = Column(String(50), nullable=True)
    is_default = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    transaction_type = Column(Enum(TransactionType), nullable=False, default=TransactionType.EXPENSE)
    amount = Column(Float, nullable=False)
    category = Column(String(50), nullable=False, default="other", index=True)
    description = Column(String(255), nullable=True)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    account = relationship("Account", back_populates="transactions")
