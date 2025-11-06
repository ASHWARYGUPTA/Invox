# /backend/app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from app.core.config import settings

# Create the engine with connection pool settings
# These settings help prevent "SSL connection has been closed unexpectedly" errors
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using them
    pool_recycle=300,    # Recycle connections after 5 minutes
    pool_size=5,         # Number of connections to maintain
    max_overflow=10,     # Maximum overflow connections
    echo=False,          # Set to True for SQL query logging
)

# Create a session "factory"
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)