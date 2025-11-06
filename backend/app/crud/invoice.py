# /backend/app/crud/invoice.py
from sqlalchemy.orm import Session
from app.models.invoice import Invoice
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate
from typing import Optional

def check_duplicate_invoice(db: Session, invoice: InvoiceCreate, owner_id: int) -> Optional[Invoice]:
    """
    Checks if an invoice with the same invoice_id and vendor_name already exists for this user.
    Returns the existing invoice if found, None otherwise.
    """
    # Only check if we have both invoice_id and vendor_name
    if not invoice.invoice_id or not invoice.vendor_name:
        return None
    
    existing = db.query(Invoice).filter(
        Invoice.owner_id == owner_id,
        Invoice.invoice_id == invoice.invoice_id,
        Invoice.vendor_name == invoice.vendor_name
    ).first()
    
    return existing

def create_invoice(db: Session, invoice: InvoiceCreate, owner_id: int, skip_duplicate_check: bool = False):
    """
    Creates a new invoice record in the database, linked to a user.
    Checks for duplicates by default (invoice_id + vendor_name).
    
    Args:
        db: Database session
        invoice: Invoice data to create
        owner_id: ID of the user who owns this invoice
        skip_duplicate_check: If True, skips duplicate checking (default: False)
    
    Returns:
        Tuple of (invoice, is_duplicate: bool)
        - invoice: The created or existing invoice
        - is_duplicate: True if returning existing invoice, False if newly created
    """
    # Check for duplicates unless explicitly skipped
    if not skip_duplicate_check:
        existing = check_duplicate_invoice(db, invoice, owner_id)
        if existing:
            return existing, True  # Return the existing invoice and flag as duplicate
    
    db_invoice = Invoice(
        **invoice.model_dump(),  # Use model_dump() instead of dict()
        owner_id=owner_id
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice, False  # Return new invoice and flag as not duplicate


def update_invoice(db: Session, db_invoice: Invoice, invoice_in: InvoiceUpdate) -> Invoice:
    """
    Updates an invoice in the database.
    """
    # Get the data from the Pydantic model
    update_data = invoice_in.model_dump(exclude_unset=True)
    
    # Update the fields
    for key, value in update_data.items():
        setattr(db_invoice, key, value)
    
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice

def get_invoices_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
    """
    Gets all invoices for a specific user.
    """
    return db.query(Invoice).filter(Invoice.owner_id == owner_id).offset(skip).limit(limit).all()

def get_invoice_by_id(db: Session, invoice_id: int):
    """
    Gets a single invoice by its primary key ID.
    """
    return db.query(Invoice).filter(Invoice.id == invoice_id).first()