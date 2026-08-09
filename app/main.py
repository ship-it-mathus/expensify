from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.config import settings
from app.database import engine, Base
from app.routers import accounts, transactions, categories, analytics

# Create database tables automatically if they don't exist yet
Base.metadata.create_all(bind=engine)

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

# Mount Angular production frontend if dist directory exists
FRONTEND_DIST_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "expensify-angular", "dist", "expensify-angular", "browser")
)

if os.path.exists(FRONTEND_DIST_DIR):
    @app.get("/{full_path:path}", tags=["Frontend SPA"])
    def serve_frontend(full_path: str):
        if full_path.startswith("api/") or full_path == "docs" or full_path == "openapi.json" or full_path == "redoc":
            return None
        file_path = os.path.join(FRONTEND_DIST_DIR, full_path)
        if full_path and os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(FRONTEND_DIST_DIR, "index.html"))
