"""
Pydantic schemas for invoice requests and responses
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class InvoiceStatus(str, Enum):
    """Invoice processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# --- Gemini AI Response Schema (from processing_service.py) ---
class InvoiceExtractionResponse(BaseModel):
    """
    Schema matching the exact format returned by Gemini AI
    This is what we get from the AI extraction
    """
    invoice_id: Optional[str] = None
    vendor_name: Optional[str] = None
    amount_due: Optional[float] = None
    due_date: Optional[str] = None  # YYYY-MM-DD format
    invoice_date: Optional[str] = None  # YYYY-MM-DD format
    currency_code: Optional[str] = "USD"
    confidence_score: float = 0.0
    
    class Config:
        json_schema_extra = {
            "example": {
                "invoice_id": "INV-2023-001",
                "vendor_name": "Acme Corporation",
                "amount_due": 1250.50,
                "due_date": "2023-12-31",
                "invoice_date": "2023-12-01",
                "currency_code": "USD",
                "confidence_score": 0.95
            }
        }


# --- Invoice Item Schema ---
class InvoiceItemBase(BaseModel):
    """Base schema for invoice line items"""
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    total_price: Optional[float] = None


class InvoiceItemCreate(InvoiceItemBase):
    """Schema for creating invoice items"""
    pass


class InvoiceItem(InvoiceItemBase):
    """Schema for invoice item response"""
    id: str
    invoice_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# --- Invoice Schemas ---
class InvoiceBase(BaseModel):
    """Base invoice schema with common fields"""
    invoice_id: Optional[str] = None
    vendor_name: Optional[str] = None
    amount_due: Optional[float] = None
    due_date: Optional[str] = None
    invoice_date: Optional[str] = None
    currency_code: Optional[str] = "USD"
    notes: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    """Schema for creating a new invoice (from upload)"""
    original_filename: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None


class InvoiceUpdate(BaseModel):
    """Schema for updating invoice fields"""
    invoice_id: Optional[str] = None
    vendor_name: Optional[str] = None
    amount_due: Optional[float] = None
    due_date: Optional[str] = None
    invoice_date: Optional[str] = None
    currency_code: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[InvoiceStatus] = None


class Invoice(InvoiceBase):
    """Complete invoice schema for response"""
    id: str
    user_id: str
    confidence_score: float
    original_filename: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    file_path: Optional[str] = None
    status: InvoiceStatus
    processing_error: Optional[str] = None
    extracted_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None
    items: List[InvoiceItem] = []
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "user-123",
                "invoice_id": "INV-2023-001",
                "vendor_name": "Acme Corporation",
                "amount_due": 1250.50,
                "due_date": "2023-12-31",
                "invoice_date": "2023-12-01",
                "currency_code": "USD",
                "confidence_score": 0.95,
                "original_filename": "invoice.pdf",
                "file_size": 102400,
                "file_type": "pdf",
                "status": "completed",
                "created_at": "2023-11-08T10:00:00",
                "updated_at": "2023-11-08T10:05:00",
                "processed_at": "2023-11-08T10:05:00"
            }
        }


class InvoiceList(BaseModel):
    """Schema for paginated invoice list"""
    total: int
    invoices: List[Invoice]
    page: int = 1
    page_size: int = 10


class InvoiceUploadResponse(BaseModel):
    """Response after uploading an invoice"""
    message: str
    invoice: Invoice
    extraction_data: InvoiceExtractionResponse
