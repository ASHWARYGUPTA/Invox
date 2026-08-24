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
    
    # OpenRouter API (for invoice processing)
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL_NAME: str = "mistralai/mistral-7b-instruct:free"
    LLM_MODEL: Optional[str] = "mistralai/mistral-7b-instruct:free"
    OPENROUTER_EMBEDDING_MODEL: Optional[str] = "nvidia/nemotron-3-embed-1b:free"
    OPENROUTER_FALLBACK_MODELS: Optional[str] = "meta-llama/llama-3.1-8b-instruct:free,microsoft/phi-3-mini-128k-instruct:free"
    
    # Encryption (for email credentials)
    ENCRYPTION_KEY: Optional[str] = None
    
    # CORS - Frontend URLs (comma-separated in .env file)
    FRONTEND_URLS: str = "http://localhost:3000,http://127.0.0.1:3000,https://invox-sandy.vercel.app"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()  # type: ignore  # Reads from .env file
print(settings.FRONTEND_URLS)
# Parse CORS origins from comma-separated FRONTEND_URLS
BACKEND_CORS_ORIGINS = [url.strip() for url in settings.FRONTEND_URLS.split(",") if url.strip()]
