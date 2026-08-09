from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Account, AccountType, Transaction, TransactionType, User
from app.auth import get_current_user
from app.schemas import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    CategoryBreakdownResponse,
    CategoryItem,
    TransferCreate,
    TransferResponse
)

router = APIRouter(prefix="/api/v1", tags=["Transactions & Transfers"])

def _require_user(current_user: Optional[User]) -> User:
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return current_user

def adjust_account_balance(account: Account, amount: float, tx_type: TransactionType, is_reversal: bool = False):
    """
    Adjusts account balance based on AccountType (Bank vs Credit Card) and TransactionType (Income vs Expense).
    If is_reversal=True, reverses the operation (used when deleting a transaction).
    """
    is_expense = (tx_type == TransactionType.EXPENSE)
    if is_reversal:
        is_expense = not is_expense

    if account.account_type == AccountType.BANK:
        account.balance += (-amount if is_expense else amount)
    elif account.account_type == AccountType.CREDIT_CARD:
        account.balance += (amount if is_expense else -amount)

@router.post(
    "/transactions",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Log Income or Expense Transaction (Auto Balance Update)"
)
def create_transaction(
    tx_in: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Logs a transaction and automatically updates the target Account's balance:
    - Expense on Bank Account ➔ Bank balance DECREASES (-amount)
    - Income on Bank Account ➔ Bank balance INCREASES (+amount)
    - Expense on Credit Card ➔ Credit Card due INCREASES (+amount)
    - Income/Payment on Credit Card ➔ Credit Card due DECREASES (-amount)
    """
    user = _require_user(current_user)
    account = db.query(Account).filter(Account.id == tx_in.account_id, Account.user_id == user.id).first()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Account with ID {tx_in.account_id} not found")

    adjust_account_balance(account, tx_in.amount, tx_in.transaction_type, is_reversal=False)

    db_tx = Transaction(**tx_in.model_dump(), user_id=user.id)
    db.add(db_tx)
    db.commit()
    db.refresh(db_tx)
    db.refresh(account)
    return db_tx


@router.post(
    "/transfers",
    response_model=TransferResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Transfer Money Between Accounts (e.g. Bank ➔ Credit Card Bill Payment)"
)
def create_transfer(
    transfer_in: TransferCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Executes an atomic transfer between two accounts:
    - Deducts/adjusts source account balance (e.g. Bank balance decreases).
    - Credit/adjusts destination account balance (e.g. Credit Card due decreases for bill payment).
    - Creates linked Outflow and Inflow transaction records for audit history.
    """
    user = _require_user(current_user)

    from_acc = db.query(Account).filter(Account.id == transfer_in.from_account_id, Account.user_id == user.id).first()
    if not from_acc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Source Account with ID {transfer_in.from_account_id} not found")

    to_acc = db.query(Account).filter(Account.id == transfer_in.to_account_id, Account.user_id == user.id).first()
    if not to_acc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Destination Account with ID {transfer_in.to_account_id} not found")

    amount = transfer_in.amount
    tx_date = transfer_in.date or datetime.now(timezone.utc)
    desc_note = transfer_in.description or "Account Transfer"

    if from_acc.account_type == AccountType.BANK and to_acc.account_type == AccountType.CREDIT_CARD:
        transfer_tag = "Credit Card Bill Payment"
    elif from_acc.account_type == AccountType.BANK and to_acc.account_type == AccountType.BANK:
        transfer_tag = "Self Fund Transfer"
    elif from_acc.account_type == AccountType.CREDIT_CARD and to_acc.account_type == AccountType.BANK:
        transfer_tag = "Card Cash Advance"
    else:
        transfer_tag = "Account Transfer"

    if from_acc.account_type == AccountType.BANK:
        from_acc.balance -= amount
    elif from_acc.account_type == AccountType.CREDIT_CARD:
        from_acc.balance += amount

    if to_acc.account_type == AccountType.BANK:
        to_acc.balance += amount
    elif to_acc.account_type == AccountType.CREDIT_CARD:
        to_acc.balance -= amount

    outflow_tx = Transaction(
        account_id=from_acc.id,
        user_id=user.id,
        transaction_type=TransactionType.EXPENSE,
        amount=amount,
        category="transfer",
        description=f"[{transfer_tag}] Transfer to {to_acc.name} ({desc_note})",
        date=tx_date
    )

    inflow_tx = Transaction(
        account_id=to_acc.id,
        user_id=user.id,
        transaction_type=TransactionType.INCOME,
        amount=amount,
        category="transfer",
        description=f"[{transfer_tag}] Transfer from {from_acc.name} ({desc_note})",
        date=tx_date
    )

    db.add_all([outflow_tx, inflow_tx])
    db.commit()
    db.refresh(from_acc)
    db.refresh(to_acc)
    db.refresh(outflow_tx)
    db.refresh(inflow_tx)

    return TransferResponse(
        message=f"Successfully transferred {amount} from {from_acc.name} to {to_acc.name}",
        amount=amount,
        transfer_tag=transfer_tag,
        from_account_id=from_acc.id,
        from_account_name=from_acc.name,
        from_account_new_balance=round(from_acc.balance, 2),
        to_account_id=to_acc.id,
        to_account_name=to_acc.name,
        to_account_new_balance=round(to_acc.balance, 2),
        outflow_transaction_id=outflow_tx.id,
        inflow_transaction_id=inflow_tx.id,
        date=tx_date
    )


@router.get(
    "/transactions",
    response_model=List[TransactionResponse],
    summary="List Transactions"
)
def list_transactions(
    account_id: Optional[str] = None,
    category: Optional[str] = None,
    transaction_type: Optional[TransactionType] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    user = _require_user(current_user)
    query = db.query(Transaction).filter(Transaction.user_id == user.id)
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
    account_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Groups all expense transactions by category and calculates spending percentages.
    Excludes internal 'transfer' category from spending breakdown.
    """
    user = _require_user(current_user)
    query = db.query(
        Transaction.category,
        func.sum(Transaction.amount).label("total_amount")
    ).filter(
        Transaction.user_id == user.id,
        Transaction.transaction_type == TransactionType.EXPENSE,
        Transaction.category != "transfer"
    )

    if account_id is not None:
        query = query.filter(Transaction.account_id == account_id)

    results = query.group_by(Transaction.category).all()

    total_expense = sum(row.total_amount for row in results) if results else 0.0

    categories = []
    if total_expense > 0:
        for row in results:
            cat_total = float(row.total_amount)
            pct = round((cat_total / total_expense) * 100, 2)
            categories.append(CategoryItem(category=row.category, total_amount=round(cat_total, 2), percentage=pct))

    return CategoryBreakdownResponse(total_expense=round(total_expense, 2), categories=categories)

@router.get(
    "/transactions/{transaction_id}",
    response_model=TransactionResponse,
    summary="Get Transaction Details"
)
def get_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    user = _require_user(current_user)
    tx = db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.user_id == user.id).first()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transaction with ID {transaction_id} not found")
    return tx

@router.patch(
    "/transactions/{transaction_id}",
    response_model=TransactionResponse,
    summary="Update Transaction (Adjusts Account Balances)"
)
def update_transaction(
    transaction_id: str,
    update_in: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    user = _require_user(current_user)
    tx = db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.user_id == user.id).first()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transaction with ID {transaction_id} not found")

    old_account = db.query(Account).filter(Account.id == tx.account_id, Account.user_id == user.id).first()
    if old_account:
        adjust_account_balance(old_account, tx.amount, tx.transaction_type, is_reversal=True)

    if update_in.account_id is not None:
        tx.account_id = update_in.account_id
    if update_in.transaction_type is not None:
        tx.transaction_type = update_in.transaction_type
    if update_in.amount is not None:
        tx.amount = update_in.amount
    if update_in.category is not None:
        tx.category = update_in.category
    if update_in.description is not None:
        tx.description = update_in.description
    if update_in.date is not None:
        tx.date = update_in.date

    new_account = db.query(Account).filter(Account.id == tx.account_id, Account.user_id == user.id).first()
    if not new_account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Account with ID {tx.account_id} not found")
    adjust_account_balance(new_account, tx.amount, tx.transaction_type, is_reversal=False)

    db.commit()
    db.refresh(tx)
    return tx

@router.delete(
    "/transactions/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Transaction (Reverses Balance Update)"
)
def delete_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    user = _require_user(current_user)
    tx = db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.user_id == user.id).first()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transaction with ID {transaction_id} not found")

    account = db.query(Account).filter(Account.id == tx.account_id, Account.user_id == user.id).first()
    if account:
        adjust_account_balance(account, tx.amount, tx.transaction_type, is_reversal=True)

    db.delete(tx)
    db.commit()
    return None
