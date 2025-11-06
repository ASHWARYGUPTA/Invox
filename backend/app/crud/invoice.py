# /backend/app/crud/invoice.py
from sqlalchemy.orm import Session
from app.models.invoice import Invoice
from app.schemas.invoice import InvoiceCreate

def create_invoice(db: Session, invoice: InvoiceCreate, owner_id: int):
    """
    Creates a new invoice record in the database, linked to a user.
    """
    db_invoice = Invoice(
        **invoice.model_dump(),  # Use model_dump() instead of dict()
        owner_id=owner_id
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice

def get_invoices_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
    """
    Gets all invoices for a specific user.
    """
    return db.query(Invoice).filter(Invoice.owner_id == owner_id).offset(skip).limit(limit).all()