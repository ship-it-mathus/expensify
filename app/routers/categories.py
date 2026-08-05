from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category, TransactionType
from app.schemas import CategoryCreate, CategoryResponse

router = APIRouter(prefix="/api/v1", tags=["Categories Management"])

DEFAULT_CATEGORIES = [
    # Income Categories
    {"name": "Salary", "category_type": TransactionType.INCOME, "icon": "attach_money", "is_default": True},
    {"name": "Side Hustle", "category_type": TransactionType.INCOME, "icon": "work", "is_default": True},
    {"name": "Freelance", "category_type": TransactionType.INCOME, "icon": "laptop", "is_default": True},
    {"name": "Investment", "category_type": TransactionType.INCOME, "icon": "trending_up", "is_default": True},
    {"name": "Refund", "category_type": TransactionType.INCOME, "icon": "replay", "is_default": True},
    {"name": "Other Income", "category_type": TransactionType.INCOME, "icon": "account_balance_wallet", "is_default": True},
    # Expense Categories
    {"name": "Food", "category_type": TransactionType.EXPENSE, "icon": "restaurant", "is_default": True},
    {"name": "Fuel", "category_type": TransactionType.EXPENSE, "icon": "local_gas_station", "is_default": True},
    {"name": "Rent", "category_type": TransactionType.EXPENSE, "icon": "home", "is_default": True},
    {"name": "Utilities", "category_type": TransactionType.EXPENSE, "icon": "bolt", "is_default": True},
    {"name": "Shopping", "category_type": TransactionType.EXPENSE, "icon": "shopping_bag", "is_default": True},
    {"name": "Entertainment", "category_type": TransactionType.EXPENSE, "icon": "movie", "is_default": True},
    {"name": "Health", "category_type": TransactionType.EXPENSE, "icon": "medical_services", "is_default": True},
    {"name": "Transport", "category_type": TransactionType.EXPENSE, "icon": "directions_bus", "is_default": True},
    {"name": "Other Expense", "category_type": TransactionType.EXPENSE, "icon": "receipt", "is_default": True},
]

def seed_default_categories(db: Session):
    """Utility to seed default Paisa categories if categories table is empty."""
    count = db.query(Category).count()
    if count == 0:
        for cat in DEFAULT_CATEGORIES:
            db.add(Category(**cat))
        db.commit()

@router.get(
    "/categories",
    response_model=List[CategoryResponse],
    summary="List Categories (Filter by Income vs Expense)"
)
def list_categories(
    category_type: Optional[TransactionType] = None,
    db: Session = Depends(get_db)
):
    seed_default_categories(db)
    query = db.query(Category)
    if category_type is not None:
        query = query.filter(Category.category_type == category_type)
    return query.order_by(Category.is_default.desc(), Category.name.asc()).all()

@router.post(
    "/categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Custom Category"
)
def create_category(
    category_in: CategoryCreate,
    db: Session = Depends(get_db)
):
    seed_default_categories(db)
    # Check duplicate
    existing = db.query(Category).filter(
        Category.name.ilike(category_in.name),
        Category.category_type == category_in.category_type
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category '{category_in.name}' already exists for type {category_in.category_type.value}"
        )

    db_cat = Category(
        name=category_in.name.strip(),
        category_type=category_in.category_type,
        icon=category_in.icon or "tag",
        is_default=False
    )
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat

@router.delete(
    "/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Custom Category"
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )
    if cat.is_default:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete system default categories"
        )

    db.delete(cat)
    db.commit()
    return None
