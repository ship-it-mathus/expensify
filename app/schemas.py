from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from app.models import AccountType

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
