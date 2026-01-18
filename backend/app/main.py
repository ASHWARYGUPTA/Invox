from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from app.core.config import settings, BACKEND_CORS_ORIGINS
from app.api.v1.api import api_router
from app.db.session import engine
from app.db.base import Base
from app.workers import start_background_polling, stop_background_polling

# Create tables
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan event handler
    Background email polling is NOT started automatically on startup.
    Users must manually trigger polling via the /email-config/poll-now endpoint
    or enable automatic polling per user via email configuration settings.
    """
    # Startup: No automatic polling
    # polling_task = asyncio.create_task(start_background_polling())
    
    yield
    
    # Shutdown: Stop any running polling workers
    stop_background_polling()
    # polling_task.cancel()
    # try:
    #     await polling_task
    # except asyncio.CancelledError:
    #     pass


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Invox Backend API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
