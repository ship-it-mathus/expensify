import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Expensify API"
    PROJECT_VERSION: str = "1.0.0"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./expensify.db")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://herwthbqakaupwatlxbh.supabase.co")
    SUPABASE_SECRET: str = os.getenv("SUPABASE_SECRET", "")
    SUPABASE_JWT_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "")

settings = Settings()
