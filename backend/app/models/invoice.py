# /backend/app/models/invoice.py
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String)
    invoice_id = Column(String, index=True, nullable=True)
    vendor_name = Column(String, index=True, nullable=True)
    amount_due = Column(Float, nullable=True)
    due_date = Column(Date, nullable=True)
    invoice_date = Column(Date, nullable=True)  # New field
    currency_code = Column(String(3), nullable=True, default="USD")  # New field: ISO 4217 (3 chars)
    confidence_score = Column(Float)
    status = Column(String, default="needs_review", index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign Key to link to the User
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # This creates the link back to the User model
    owner = relationship("User")

