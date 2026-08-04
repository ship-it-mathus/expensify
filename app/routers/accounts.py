from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Account, AccountType
from app.schemas import AccountCreate, AccountUpdate, AccountResponse, NetWorthSummary

router = APIRouter(prefix="/api/v1", tags=["Accounts & Net Worth"])

@router.get("/summary", response_model=NetWorthSummary, summary="Calculate Net Available Money")
def get_net_worth_summary(db: Session = Depends(get_db)):
    """
    Calculates your actual liquid money:
    (Sum of Included Bank Balances) - (Sum of Included Credit Card Dues)
    Accounts marked with `include_in_net_worth = False` are excluded automatically.
    """
    accounts = db.query(Account).all()
    
    total_bank = 0.0
    total_credit_card = 0.0
    included_count = 0
    excluded_count = 0

    for acc in accounts:
        if acc.include_in_net_worth:
            included_count += 1
            if acc.account_type == AccountType.BANK:
                total_bank += acc.balance
            elif acc.account_type == AccountType.CREDIT_CARD:
                total_credit_card += acc.balance
        else:
            excluded_count += 1

    actual_liquid = total_bank - total_credit_card

    return NetWorthSummary(
        total_bank_balance=round(total_bank, 2),
        total_credit_card_dues=round(total_credit_card, 2),
        actual_liquid_money=round(actual_liquid, 2),
        included_accounts_count=included_count,
        excluded_accounts_count=excluded_count,
        currency="INR"
    )

@router.post("/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED, summary="Create New Account")
def create_account(account_in: AccountCreate, db: Session = Depends(get_db)):
    db_account = Account(**account_in.model_dump())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

@router.get("/accounts", response_model=List[AccountResponse], summary="Get All Accounts")
def list_accounts(
    include_in_net_worth: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Account)
    if include_in_net_worth is not None:
        query = query.filter(Account.include_in_net_worth == include_in_net_worth)
    return query.all()

@router.get("/accounts/{account_id}", response_model=AccountResponse, summary="Get Account Details")
def get_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with ID {account_id} not found"
        )
    return account

@router.patch("/accounts/{account_id}", response_model=AccountResponse, summary="Update Account Details / Toggle Exclusion")
def update_account(
    account_id: int,
    account_in: AccountUpdate,
    db: Session = Depends(get_db)
):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with ID {account_id} not found"
        )
    
    update_data = account_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(account, field, value)
        
    db.commit()
    db.refresh(account)
    return account

@router.delete("/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Account")
def delete_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with ID {account_id} not found"
        )
    db.delete(account)
    db.commit()
    return None
