import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db
from app.auth import get_current_user
from app.models import User

# Use in-memory SQLite database for test isolation
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

TEST_USER_ID = "test-user-id-001"
TEST_USER_EMAIL = "test@expensify.local"

@pytest.fixture(scope="function")
def db_session():
    """Fixture that creates clean database tables for each test and rolls back after."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    # Ensure test user exists in DB
    if not db.query(User).filter(User.id == TEST_USER_ID).first():
        db.add(User(id=TEST_USER_ID, email=TEST_USER_EMAIL))
        db.commit()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Fixture that provides a FastAPI TestClient with db and auth dependency overridden."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_get_current_user():
        # Always return a fresh User instance from the active session
        return db_session.query(User).filter(User.id == TEST_USER_ID).first()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
