from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.models import AccountType, TransactionType

# Account Schemas
class AccountBase(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "HDFC Savings Account"})
    account_type: AccountType = Field(..., json_schema_extra={"example": AccountType.BANK})
    balance: float = Field(default=0.0, description="Bank balance or Credit Card due amount", json_schema_extra={"example": 50000.0})
    include_in_net_worth: bool = Field(default=True, description="Set to False for Emergency Fund or hidden accounts")
    currency: str = Field(default="INR", json_schema_extra={"example": "INR"})
    notes: Optional[str] = Field(default=None, json_schema_extra={"example": "Main salary account"})

class AccountCreate(AccountBase):
    pass

class AccountUpdate(BaseModel):
    name: Optional[str] = None
    account_type: Optional[AccountType] = None
    balance: Optional[float] = None
    include_in_net_worth: Optional[bool] = None
    currency: Optional[str] = None
    notes: Optional[str] = None

class AccountResponse(AccountBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class NetWorthSummary(BaseModel):
    total_bank_balance: float = Field(..., description="Sum of active Bank Accounts included in calculation")
    total_credit_card_dues: float = Field(..., description="Sum of active Credit Card Dues included in calculation")
    actual_liquid_money: float = Field(..., description="Net Money (Bank Balance - Credit Card Dues)")
    included_accounts_count: int = Field(..., description="Number of accounts included in calculation")
    excluded_accounts_count: int = Field(..., description="Number of accounts hidden/excluded from calculation")
    currency: str = Field(default="INR")

# Transaction Schemas
class TransactionBase(BaseModel):
    account_id: int = Field(..., description="Target Account ID for this transaction")
    transaction_type: TransactionType = Field(default=TransactionType.EXPENSE, json_schema_extra={"example": TransactionType.EXPENSE})
    amount: float = Field(..., gt=0, description="Positive transaction amount", json_schema_extra={"example": 450.0})
    category: str = Field(default="food", json_schema_extra={"example": "food"}, description="e.g. food, salary, rent, shopping, utilities, transfer, bill_payment")
    description: Optional[str] = Field(default=None, json_schema_extra={"example": "Dinner with friends"})
    date: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc), description="Transaction timestamp")

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CategoryItem(BaseModel):
    category: str
    total_amount: float
    percentage: float

class CategoryBreakdownResponse(BaseModel):
    total_expense: float
    categories: List[CategoryItem]

# Transfer Schemas
class TransferCreate(BaseModel):
    from_account_id: int = Field(..., description="Source Account ID (e.g. Bank Account)", json_schema_extra={"example": 1})
    to_account_id: int = Field(..., description="Destination Account ID (e.g. Credit Card for bill payment)", json_schema_extra={"example": 2})
    amount: float = Field(..., gt=0, description="Transfer amount", json_schema_extra={"example": 10000.0})
    description: Optional[str] = Field(default=None, json_schema_extra={"example": "Credit Card Bill Payment"})
    date: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))

    @model_validator(mode="after")
    def check_different_accounts(self):
        if self.from_account_id == self.to_account_id:
            raise ValueError("from_account_id and to_account_id cannot be the same account.")
        return self

class TransferResponse(BaseModel):
    message: str
    amount: float
    from_account_id: int
    from_account_name: str
    from_account_new_balance: float
    to_account_id: int
    to_account_name: str
    to_account_new_balance: float
    outflow_transaction_id: int
    inflow_transaction_id: int
    date: datetime
