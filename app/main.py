from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.config import settings
from app.database import engine, Base
from app.routers import accounts, transactions, categories, analytics
from sqlalchemy import text

# Create database tables automatically if they don't exist yet
Base.metadata.create_all(bind=engine)

def run_startup_migrations():
    """Auto-applies schema updates to production PostgreSQL (Supabase)."""
    if settings.DATABASE_URL.startswith("sqlite"):
        return
    with engine.connect() as conn:
        # Add parent_id column to categories table if missing
        try:
            conn.execute(text("ALTER TABLE categories ADD COLUMN IF NOT EXISTS parent_id VARCHAR(26) REFERENCES categories(id) ON DELETE SET NULL;"))
            conn.commit()
        except Exception as e:
            print(f"[Migration] categories.parent_id notice: {e}")

        # Add user_id to tables if missing
        for table in ["accounts", "transactions", "categories"]:
            try:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS user_id VARCHAR(36) REFERENCES users(id) ON DELETE CASCADE;"))
                conn.commit()
            except Exception as e:
                print(f"[Migration] {table}.user_id notice: {e}")

        # Add 'investment' enum value to PostgreSQL accounttype enum
        try:
            conn.execution_options(isolation_level="AUTOCOMMIT").execute(text("ALTER TYPE accounttype ADD VALUE IF NOT EXISTS 'investment';"))
        except Exception as e:
            print(f"[Migration] accounttype enum notice: {e}")

try:
    run_startup_migrations()
except Exception as e:
    print(f"[Migration Error] Startup migration notice: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Expensify REST API - Live Expense, Transactions, Categories & Net Available Money Tracker."
)

# Enable CORS for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Check Route
@app.get("/api/v1/health", tags=["Health Check"])
@app.get("/api/health", tags=["Health Check"])
def health_check():
    return {
        "status": "online",
        "message": "Welcome to Expensify REST API!",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

# Register API Routers
app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(categories.router)
app.include_router(analytics.router)

# Mount bundled static Angular frontend if app/static exists
STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "static"))

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/{full_path:path}", tags=["Frontend SPA"])
    def serve_frontend(full_path: str):
        if full_path.startswith("api/") or full_path == "docs" or full_path == "openapi.json" or full_path == "redoc":
            return None
        file_path = os.path.join(STATIC_DIR, full_path)
        if full_path and os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))
