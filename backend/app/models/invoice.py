# /backend/app/models/invoice.py
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String)
    invoice_id = Column(String, index=True, nullable=True)
    vendor_name = Column(String, index=True, nullable=True)
    amount_due = Column(Float, nullable=True)
    due_date = Column(Date, nullable=True)
    confidence_score = Column(Float)
    
    # Foreign Key to link to the User
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # This creates the link back to the User model
    owner = relationship("User")