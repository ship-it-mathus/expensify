import jwt
import pytest
from app.auth import get_current_user
from app.models import User

def test_tc_usr_001_create_user_model(db_session):
    """TC-USR-001: Verifies creation and querying of User model."""
    user = User(id="usr_test_123", email="testuser@expensify.com", full_name="Test User")
    db_session.add(user)
    db_session.commit()

    fetched = db_session.query(User).filter(User.id == "usr_test_123").first()
    assert fetched is not None
    assert fetched.email == "testuser@expensify.com"
    assert fetched.full_name == "Test User"

def test_tc_usr_002_auth_dependency_header(db_session):
    """TC-USR-002: Verifies get_current_user dependency provisions user via X-User-ID header."""
    user = get_current_user(x_user_id="usr_dev_header", db=db_session)
    assert user is not None
    assert user.id == "usr_dev_header"
    assert "usr_dev_header" in user.email

def test_tc_usr_003_auth_dependency_jwt(db_session):
    """TC-USR-003: Verifies get_current_user dependency decodes JWT Bearer token."""
    token = jwt.encode({"sub": "usr_supabase_uuid", "email": "supabase@user.com"}, "secret_key_32_bytes_minimum_length_for_sha256", algorithm="HS256")
    user = get_current_user(authorization=f"Bearer {token}", db=db_session)
    assert user is not None
    assert user.id == "usr_supabase_uuid"
    assert user.email == "supabase@user.com"
