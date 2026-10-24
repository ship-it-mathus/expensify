from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import extract, func

from app.database import get_db
from app.models import Transaction, TransactionType, AccountType, Account, User
from app.auth import get_current_user
from app.schemas import MonthlyAnalyticsResponse, CategoryItem, InvestmentAnalyticsResponse, AssetAllocationSlice

router = APIRouter(prefix="/api/v1", tags=["Analytics & Insights"])

@router.get(
    "/analytics/monthly",
    response_model=MonthlyAnalyticsResponse,
    summary="Income vs Expense & Savings Analytics (Scoped by Day, Month, or Year)"
)
def get_monthly_analytics(
    scope: Optional[str] = "month",
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    now = datetime.now(timezone.utc)
    target_year = year or now.year
    target_month = month or now.month
    target_day = day or now.day
    target_scope = (scope or "month").lower()

    # Build date filters based on scope
    date_filters = [
        Transaction.user_id == current_user.id,
        Transaction.category != "transfer",
        Transaction.is_transfer == False,
        extract("year", Transaction.date) == target_year
    ]

    if target_scope in ("month", "day"):
        date_filters.append(extract("month", Transaction.date) == target_month)
    if target_scope == "day":
        date_filters.append(extract("day", Transaction.date) == target_day)

    # 1. Total Income for this user
    income_query = db.query(func.sum(Transaction.amount)).filter(
        *date_filters,
        Transaction.transaction_type == TransactionType.INCOME
    ).scalar()
    total_income = float(income_query) if income_query else 0.0

    # 2. Total Expense for this user
    expense_query = db.query(func.sum(Transaction.amount)).filter(
        *date_filters,
        Transaction.transaction_type == TransactionType.EXPENSE
    ).scalar()
    total_expense = float(expense_query) if expense_query else 0.0

    # 3. Net Savings & Savings Rate
    net_savings = total_income - total_expense
    savings_rate = round((net_savings / total_income) * 100, 2) if total_income > 0 else 0.0

    # 4. Category Breakdown for the Scope
    cat_query = db.query(
        Transaction.category,
        func.sum(Transaction.amount).label("cat_total")
    ).filter(
        *date_filters,
        Transaction.transaction_type == TransactionType.EXPENSE
    ).group_by(Transaction.category).all()

    categories = []
    if total_expense > 0:
        for row in cat_query:
            amt = float(row.cat_total)
            pct = round((amt / total_expense) * 100, 2)
            categories.append(CategoryItem(category=row.category, total_amount=round(amt, 2), percentage=pct))

    return MonthlyAnalyticsResponse(
        scope=target_scope,
        year=target_year,
        month=target_month,
        day=target_day if target_scope == "day" else None,
        total_income=round(total_income, 2),
        total_expense=round(total_expense, 2),
        net_savings=round(net_savings, 2),
        savings_rate_percentage=savings_rate,
        categories=categories
    )


@router.get(
    "/analytics/investment",
    response_model=InvestmentAnalyticsResponse,
    summary="Investment Analytics — % of Income Invested"
)
def get_investment_analytics(
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    now = datetime.now(timezone.utc)
    target_year = year or now.year
    target_month = month or now.month

    # Total invested = sum of INCOME (inflow) transactions to investment accounts this month.
    # When you transfer Bank → Investment, an INCOME/transfer tx is created on the investment account.
    investment_account_ids = [
        acc.id for acc in db.query(Account).filter(
            Account.user_id == current_user.id,
            Account.account_type == AccountType.INVESTMENT
        ).all()
    ]

    total_invested = 0.0
    if investment_account_ids:
        invested_query = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == current_user.id,
            Transaction.account_id.in_(investment_account_ids),
            Transaction.transaction_type == TransactionType.INCOME,
            Transaction.category == "transfer",
            extract("year", Transaction.date) == target_year,
            extract("month", Transaction.date) == target_month
        ).scalar()
        total_invested = float(invested_query) if invested_query else 0.0

    # Total income this month (for % calculation)
    income_query = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == TransactionType.INCOME,
        Transaction.category != "transfer",
        extract("year", Transaction.date) == target_year,
        extract("month", Transaction.date) == target_month
    ).scalar()
    total_income = float(income_query) if income_query else 0.0

    pct = round((total_invested / total_income) * 100, 2) if total_income > 0 else 0.0

    # Current total value & asset allocation across all investment accounts
    user_accounts = db.query(Account).filter(Account.user_id == current_user.id).all()
    
    total_bank = 0.0
    total_credit_card = 0.0
    total_investment_balance = 0.0
    allocations_map = {}

    for acc in user_accounts:
        if acc.account_type == AccountType.INVESTMENT:
            total_investment_balance += acc.balance
            cls = acc.asset_class or "other"
            allocations_map[cls] = allocations_map.get(cls, 0.0) + acc.balance
        elif acc.include_in_net_worth:
            if acc.account_type == AccountType.BANK:
                total_bank += acc.balance
            elif acc.account_type == AccountType.CREDIT_CARD:
                total_credit_card += acc.balance

    liquid_money = total_bank - total_credit_card
    total_portfolio_wealth = liquid_money + total_investment_balance

    asset_allocation = []
    if total_investment_balance > 0:
        for cls, amt in sorted(allocations_map.items(), key=lambda x: x[1], reverse=True):
            slice_pct = round((amt / total_investment_balance) * 100, 1)
            asset_allocation.append(
                AssetAllocationSlice(
                    asset_class=cls,
                    amount=round(amt, 2),
                    percentage=slice_pct
                )
            )

    return InvestmentAnalyticsResponse(
        year=target_year,
        month=target_month,
        total_invested=round(total_invested, 2),
        total_income=round(total_income, 2),
        pct_income_invested=pct,
        total_investment_balance=round(total_investment_balance, 2),
        total_portfolio_wealth=round(total_portfolio_wealth, 2),
        asset_allocation=asset_allocation
    )

