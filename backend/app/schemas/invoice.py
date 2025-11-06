# /backend/app/schemas/invoice.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date, datetime

class InvoiceBase(BaseModel):
    file_name: str
    invoice_id: Optional[str] = None
    vendor_name: Optional[str] = None
    amount_due: Optional[float] = None
    due_date: Optional[date] = None
    invoice_date: Optional[date] = None
    currency_code: Optional[str] = Field(default="USD", max_length=3)
    confidence_score: Optional[float] = None
    status: Optional[str] = "needs_review"

class InvoiceCreate(InvoiceBase):
    pass

class Invoice(InvoiceBase):
    id: int
    owner_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class InvoiceUpdate(BaseModel):
    invoice_id: Optional[str] = None
    vendor_name: Optional[str] = None
    amount_due: Optional[float] = None
    due_date: Optional[date] = None
    status: Optional[str] = None
    
    class Config:
        from_attributes = True