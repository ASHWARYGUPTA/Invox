# /backend/app/core/config.py
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', '.env'))

class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "Invoice AI"

    # Database
    # Format: "postgresql://USER:PASSWORD@HOST/DB_NAME"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:your_password@localhost/invoice_db")

    # Google
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    # NEW Google OAuth "Web App" Credentials (we will get these later)
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "a_very_secret_key_change_this")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # One day
    
    class Config:
        case_sensitive = True

settings = Settings()