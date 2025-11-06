# /backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.core.config import settings
from app.api.endpoints import auth
from app.api.endpoints import invoices  # 1. Import

# ...
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/api/v1/openapi.json"
)

# CORS Configuration - Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Your React frontend
        "http://localhost:3001",  # Your friend's Next.js (if different port)
        "http://127.0.0.1:3000",
        "*"  # Allow all origins (for development with ngrok)
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers (like Authorization)
)

# 2. Add routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(invoices.router, prefix="/api/v1/invoices", tags=["invoices"]) # 3. Add this line

@app.get("/")
def read_root():
    return {"status": f"Welcome to {settings.PROJECT_NAME}"}