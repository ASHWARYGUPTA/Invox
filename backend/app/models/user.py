from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    """
    NextAuth compatible User model
    """
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    email_verified = Column(DateTime, nullable=True)
    image = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="user", cascade="all, delete-orphan")


class Account(Base):
    """
    NextAuth compatible Account model for OAuth providers
    """
    __tablename__ = "accounts"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String, nullable=False)  # oauth, email, credentials
    provider = Column(String, nullable=False)  # google, github, etc.
    provider_account_id = Column(String, nullable=False)
    refresh_token = Column(Text, nullable=True)
    access_token = Column(Text, nullable=True)
    expires_at = Column(Integer, nullable=True)
    token_type = Column(String, nullable=True)
    scope = Column(String, nullable=True)
    id_token = Column(Text, nullable=True)
    session_state = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="accounts")

    __table_args__ = (
        # Composite unique constraint
        {'sqlite_autoincrement': True}
    )


class Session(Base):
    """
    NextAuth compatible Session model (for database sessions)
    """
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, default=generate_uuid)
    session_token = Column(String, unique=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    expires = Column(DateTime, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="sessions")


class VerificationToken(Base):
    """
    NextAuth compatible VerificationToken model
    """
    __tablename__ = "verification_tokens"

    identifier = Column(String, primary_key=True)
    token = Column(String, primary_key=True)
    expires = Column(DateTime, nullable=False)
