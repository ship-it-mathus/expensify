from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Account, AccountType, Transaction, TransactionType
from app.schemas import (
    TransactionCreate,
    TransactionResponse,
    CategoryBreakdownResponse,
    CategoryItem
)

router = APIRouter(prefix="/api/v1", tags=["Transactions & Analytics"])

@router.post(
    "/transactions",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Log Income or Expense Transaction (Auto Balance Update)"
)
def create_transaction(
    tx_in: TransactionCreate,
    db: Session = Depends(get_db)
):
    """
    Logs a transaction and automatically updates the target Account's balance:
    - Expense on Bank Account ➔ Bank balance DECREASES (-amount)
    - Income on Bank Account ➔ Bank balance INCREASES (+amount)
    - Expense on Credit Card ➔ Credit Card due INCREASES (+amount)
    - Income/Payment on Credit Card ➔ Credit Card due DECREASES (-amount)
    """
    account = db.query(Account).filter(Account.id == tx_in.account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with ID {tx_in.account_id} not found"
        )

    # Calculate balance adjustment
    amount = tx_in.amount
    if account.account_type == AccountType.BANK:
        if tx_in.transaction_type == TransactionType.EXPENSE:
            account.balance -= amount
        else:
            account.balance += amount
    elif account.account_type == AccountType.CREDIT_CARD:
        if tx_in.transaction_type == TransactionType.EXPENSE:
            account.balance += amount
        else:
            account.balance -= amount

    # Create transaction record
    db_tx = Transaction(**tx_in.model_dump())
    db.add(db_tx)
    db.commit()
    db.refresh(db_tx)
    db.refresh(account)

    return db_tx

@router.get(
    "/transactions",
    response_model=List[TransactionResponse],
    summary="List Transactions"
)
def list_transactions(
    account_id: Optional[int] = None,
    category: Optional[str] = None,
    transaction_type: Optional[TransactionType] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Transaction)
    if account_id is not None:
        query = query.filter(Transaction.account_id == account_id)
    if category is not None:
        query = query.filter(func.lower(Transaction.category) == category.lower())
    if transaction_type is not None:
        query = query.filter(Transaction.transaction_type == transaction_type)
    
    return query.order_by(Transaction.date.desc()).all()

@router.get(
    "/transactions/analytics/categories",
    response_model=CategoryBreakdownResponse,
    summary="Category Spending Breakdown Analytics"
)
def get_category_breakdown(
    account_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Groups all expense transactions by category and calculates spending percentages.
    """
    query = db.query(
        Transaction.category,
        func.sum(Transaction.amount).label("total_amount")
    ).filter(Transaction.transaction_type == TransactionType.EXPENSE)

    if account_id is not None:
        query = query.filter(Transaction.account_id == account_id)

    results = query.group_by(Transaction.category).all()

    total_expense = sum(row.total_amount for row in results) if results else 0.0

    categories = []
    if total_expense > 0:
        for row in results:
            cat_total = float(row.total_amount)
            pct = round((cat_total / total_expense) * 100, 2)
            categories.append(
                CategoryItem(
                    category=row.category,
                    total_amount=round(cat_total, 2),
                    percentage=pct
                )
            )

    return CategoryBreakdownResponse(
        total_expense=round(total_expense, 2),
        categories=categories
    )

@router.get(
    "/transactions/{transaction_id}",
    response_model=TransactionResponse,
    summary="Get Transaction Details"
)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found"
        )
    return tx

@router.delete(
    "/transactions/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Transaction (Reverses Balance Update)"
)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found"
        )

    # Revert account balance adjustment
    account = db.query(Account).filter(Account.id == tx.account_id).first()
    if account:
        amount = tx.amount
        if account.account_type == AccountType.BANK:
            if tx.transaction_type == TransactionType.EXPENSE:
                account.balance += amount
            else:
                account.balance -= amount
        elif account.account_type == AccountType.CREDIT_CARD:
            if tx.transaction_type == TransactionType.EXPENSE:
                account.balance -= amount
            else:
                account.balance += amount

    db.delete(tx)
    db.commit()
    return None
