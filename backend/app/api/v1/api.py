from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, invoices, email_config, gmail_oauth

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(invoices.router, prefix="/invoices", tags=["invoices"])
api_router.include_router(email_config.router, prefix="/email-config", tags=["email-config"])
api_router.include_router(gmail_oauth.router, prefix="/email-config", tags=["gmail-oauth"])
