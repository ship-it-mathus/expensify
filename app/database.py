from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

def get_engine_url(raw_url: str) -> str:
    """Normalize database connection URLs and provide driver fallbacks between psycopg (v3) and psycopg2."""
    db_url = raw_url
    if db_url.startswith("postgres://"):
        # SQLAlchemy 1.4+ removed support for the legacy 'postgres://' scheme
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    if db_url.startswith("postgresql+psycopg://"):
        try:
            import psycopg  # noqa: F401
        except ImportError:
            # Fall back to psycopg2 if psycopg (v3) is not installed
            db_url = db_url.replace("postgresql+psycopg://", "postgresql+psycopg2://", 1)
    elif db_url.startswith("postgresql+psycopg2://"):
        try:
            import psycopg2  # noqa: F401
        except ImportError:
            # Fall back to psycopg (v3) if psycopg2 is not installed
            db_url = db_url.replace("postgresql+psycopg2://", "postgresql+psycopg://", 1)
    elif db_url.startswith("postgresql://"):
        try:
            import psycopg2  # noqa: F401
        except ImportError:
            try:
                import psycopg  # noqa: F401
                db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
            except ImportError:
                pass

    return db_url

db_url = get_engine_url(settings.DATABASE_URL)

# Handle SQLite specific connection requirement
engine_kwargs = {}
if db_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

# Create SQLAlchemy engine
engine = create_engine(db_url, **engine_kwargs)

# Create session maker for DB sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for database models
Base = declarative_base()

def get_db():
    """Dependency that yields a database session per request and closes it after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
