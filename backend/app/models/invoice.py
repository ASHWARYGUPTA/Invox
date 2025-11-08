"""
Invoice database models for storing extracted invoice data
"""
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.db.base import Base


class InvoiceStatus(str, enum.Enum):
    """Invoice processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Invoice(Base):
    """
    Main invoice table storing extracted invoice information
    """
    __tablename__ = "invoices"

    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # User relationship
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Extracted invoice data (from Gemini)
    invoice_id = Column(String, nullable=True, index=True)  # Invoice number from document
    vendor_name = Column(String, nullable=True, index=True)
    amount_due = Column(Float, nullable=True)
    due_date = Column(String, nullable=True)  # Stored as YYYY-MM-DD string
    invoice_date = Column(String, nullable=True)  # Stored as YYYY-MM-DD string
    currency_code = Column(String(3), nullable=True, default="USD")
    confidence_score = Column(Float, nullable=True, default=0.0)
    
    # File metadata
    original_filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=True)  # Size in bytes
    file_type = Column(String, nullable=True)  # pdf, jpg, png, etc.
    file_path = Column(String, nullable=True)  # Storage path if files are saved
    
    # Processing status
    status = Column(SQLEnum(InvoiceStatus), nullable=False, default=InvoiceStatus.PENDING)
    processing_error = Column(Text, nullable=True)
    
    # Extracted raw text (for search/reference)
    extracted_text = Column(Text, nullable=True)
    
    # Additional notes (user can add)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Invoice {self.invoice_id} - {self.vendor_name}>"


class InvoiceItem(Base):
    """
    Line items for invoices (optional, for detailed extraction)
    """
    __tablename__ = "invoice_items"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    invoice_id = Column(String, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)
    
    # Item details
    description = Column(String, nullable=True)
    quantity = Column(Float, nullable=True)
    unit_price = Column(Float, nullable=True)
    total_price = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="items")
    
    def __repr__(self):
        return f"<InvoiceItem {self.description}>"
