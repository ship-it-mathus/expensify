from typing import Optional, Union
import jwt
from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.config import settings

def get_current_user(
    authorization: Optional[str] = Header(None),
    x_user_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    FastAPI security dependency:
    1. Extracts Bearer JWT token from Authorization header or X-User-ID for dev.
    2. Decodes user sub (UUID) and email.
    3. Auto-provisions User in DB if first login.
    """
    # Guard against direct function calls passing FastAPI Header default objects
    if not isinstance(authorization, str):
        authorization = None
    if not isinstance(x_user_id, str):
        x_user_id = None

    user_id: Optional[str] = None
    email: Optional[str] = None

    # Dev fallback header
    if x_user_id:
        user_id = x_user_id
        email = f"{x_user_id}@expensify.local"
    elif authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            user_id = payload.get("sub") or payload.get("user_id")
            email = payload.get("email") or f"{user_id}@expensify.user"
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid Supabase JWT token: {str(e)}"
            )

    if not user_id:
        return None

    # Fetch or auto-create User record in DB
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(id=user_id, email=email or f"{user_id}@user.local")
        db.add(user)
        db.commit()
        db.refresh(user)

    return user
