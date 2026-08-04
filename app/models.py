import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum
from app.database import Base

class AccountType(str, enum.Enum):
    BANK = "bank"
    CREDIT_CARD = "credit_card"

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
