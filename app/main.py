from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.routers import accounts

# Create database tables automatically if they don't exist yet
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Expensify REST API - Live Expense & Net Available Money Tracker with Account Hiding Support."
)

# Enable CORS for cross-origin requests (for your future Web / Mobile app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your specific frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(accounts.router)

@app.get("/", tags=["Health Check"])
def root():
    return {
        "status": "online",
        "message": "Welcome to Expensify API!",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }
