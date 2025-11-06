# /backend/app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    hashed_password = Column(String, nullable=True)  # For potential email/pass login
    is_active = Column(Boolean, default=True)
    
    # Google OAuth fields
    google_sub = Column(String, unique=True, index=True, nullable=True)
    google_picture = Column(String, nullable=True)