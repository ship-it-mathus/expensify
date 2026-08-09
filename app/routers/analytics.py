from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import extract, func

from app.database import get_db
from app.models import Transaction, TransactionType, User
from app.auth import get_current_user
from app.schemas import MonthlyAnalyticsResponse, CategoryItem

router = APIRouter(prefix="/api/v1", tags=["Analytics & Insights"])

@router.get(
    "/analytics/monthly",
    response_model=MonthlyAnalyticsResponse,
    summary="Monthly Income vs Expense & Savings Analytics"
)
def get_monthly_analytics(
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

    # 1. Total Income for this user
    income_query = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == TransactionType.INCOME,
        Transaction.category != "transfer",
        extract("year", Transaction.date) == target_year,
        extract("month", Transaction.date) == target_month
    ).scalar()
    total_income = float(income_query) if income_query else 0.0

    # 2. Total Expense for this user
    expense_query = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == TransactionType.EXPENSE,
        Transaction.category != "transfer",
        extract("year", Transaction.date) == target_year,
        extract("month", Transaction.date) == target_month
    ).scalar()
    total_expense = float(expense_query) if expense_query else 0.0

    # 3. Net Savings & Savings Rate
    net_savings = total_income - total_expense
    savings_rate = round((net_savings / total_income) * 100, 2) if total_income > 0 else 0.0

    # 4. Category Breakdown for the Month for this user
    cat_query = db.query(
        Transaction.category,
        func.sum(Transaction.amount).label("cat_total")
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == TransactionType.EXPENSE,
        Transaction.category != "transfer",
        extract("year", Transaction.date) == target_year,
        extract("month", Transaction.date) == target_month
    ).group_by(Transaction.category).all()

    categories = []
    if total_expense > 0:
        for row in cat_query:
            amt = float(row.cat_total)
            pct = round((amt / total_expense) * 100, 2)
            categories.append(CategoryItem(category=row.category, total_amount=round(amt, 2), percentage=pct))

    return MonthlyAnalyticsResponse(
        year=target_year,
        month=target_month,
        total_income=round(total_income, 2),
        total_expense=round(total_expense, 2),
        net_savings=round(net_savings, 2),
        savings_rate_percentage=savings_rate,
        categories=categories
    )
