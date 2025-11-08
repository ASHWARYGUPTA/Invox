from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Invox Backend"
    
    # Security
    SECRET_KEY: str  # JWT secret key for authentication
    
    # NextAuth
    NEXTAUTH_URL: str
    NEXTAUTH_SECRET: str
    
    # Google OAuth (for NextAuth)
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    
    # Gmail OAuth (for email polling - can be same as above or separate)
    GMAIL_CLIENT_ID: Optional[str] = None
    GMAIL_CLIENT_SECRET: Optional[str] = None
    GMAIL_REDIRECT_URI: str = "http://localhost:3000/auth/gmail/callback"  # Override in production
    
    # Google Gemini AI (for invoice processing)
    GOOGLE_API_KEY: Optional[str] = None
    
    # Encryption (for email credentials)
    ENCRYPTION_KEY: Optional[str] = None
    
    # CORS - Frontend URLs (comma-separated in .env file)
    FRONTEND_URLS: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()  # type: ignore  # Reads from .env file

# Parse CORS origins from comma-separated FRONTEND_URLS
BACKEND_CORS_ORIGINS = [url.strip() for url in settings.FRONTEND_URLS.split(",") if url.strip()]
