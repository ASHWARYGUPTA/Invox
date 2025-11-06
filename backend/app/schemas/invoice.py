# /backend/app/schemas/invoice.py
from pydantic import BaseModel
from typing import Optional
from datetime import date

class InvoiceBase(BaseModel):
    file_name: str
    invoice_id: Optional[str] = None
    vendor_name: Optional[str] = None
    amount_due: Optional[float] = None
    due_date: Optional[date] = None
    confidence_score: Optional[float] = None

class InvoiceCreate(InvoiceBase):
    pass

class Invoice(InvoiceBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True