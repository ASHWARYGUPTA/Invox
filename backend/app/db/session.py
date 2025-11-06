# /backend/app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create the engine (the connection)
engine = create_engine(settings.DATABASE_URL)

# Create a session "factory"
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)