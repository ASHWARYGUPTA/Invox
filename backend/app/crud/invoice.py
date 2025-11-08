"""
CRUD operations for invoices
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
from app.models.invoice import Invoice, InvoiceStatus
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceExtractionResponse


def create_invoice(
    db: Session,
    user_id: str,
    invoice_data: InvoiceCreate,
    extraction_result: Optional[InvoiceExtractionResponse] = None,
    extracted_text: Optional[str] = None
) -> Invoice:
    """
    Create a new invoice in the database
    
    Args:
        db: Database session
        user_id: ID of the user who uploaded the invoice
        invoice_data: Basic invoice information
        extraction_result: AI-extracted data from Gemini
        extracted_text: Raw text extracted from the document
    
    Returns:
        Created Invoice object
    """
    
    # Extract invoice details for duplicate checking
    invoice_id = extraction_result.invoice_id if extraction_result else invoice_data.invoice_id
    vendor_name = extraction_result.vendor_name if extraction_result else invoice_data.vendor_name
    amount_due = extraction_result.amount_due if extraction_result else invoice_data.amount_due
    invoice_date = extraction_result.invoice_date if extraction_result else invoice_data.invoice_date
    
    # Strategy 1: Check for exact match on key fields (invoice_id, vendor, amount, date)
    if invoice_id and vendor_name and amount_due and invoice_date:
        existing_invoice = db.query(Invoice).filter(
            Invoice.user_id == user_id,
            Invoice.invoice_id == invoice_id,
            Invoice.vendor_name == vendor_name,
            Invoice.amount_due == amount_due,
            Invoice.invoice_date == invoice_date
        ).first()
        
        if existing_invoice:
            print(f"⚠️  Duplicate invoice detected (exact match):")
            print(f"   Invoice #: {invoice_id} | Vendor: {vendor_name}")
            print(f"   Amount: {amount_due} | Date: {invoice_date}")
            print(f"   Existing DB ID: {existing_invoice.id}")
            print(f"   ⏭️  Skipping creation to prevent duplicate")
            return existing_invoice  # Return existing invoice instead of creating duplicate
    
    # Strategy 2: Check for filename match (same file uploaded twice)
    if invoice_data.original_filename:
        existing_by_filename = db.query(Invoice).filter(
            Invoice.user_id == user_id,
            Invoice.original_filename == invoice_data.original_filename
        ).first()
        
        if existing_by_filename:
            # Double-check if it's really the same invoice by comparing amount
            if amount_due and existing_by_filename.amount_due == amount_due:
                print(f"⚠️  Duplicate invoice detected (same filename + amount):")
                print(f"   Filename: {invoice_data.original_filename}")
                print(f"   Amount: {amount_due}")
                print(f"   Existing DB ID: {existing_by_filename.id}")
                print(f"   ⏭️  Skipping creation to prevent duplicate")
                return existing_by_filename
    
    # Strategy 3: Partial match - same vendor, amount, and date (even if invoice_id differs)
    if vendor_name and amount_due and invoice_date:
        existing_partial = db.query(Invoice).filter(
            Invoice.user_id == user_id,
            Invoice.vendor_name == vendor_name,
            Invoice.amount_due == amount_due,
            Invoice.invoice_date == invoice_date
        ).first()
        
        if existing_partial:
            print(f"⚠️  Likely duplicate invoice detected (vendor + amount + date match):")
            print(f"   Vendor: {vendor_name} | Amount: {amount_due} | Date: {invoice_date}")
            print(f"   New invoice #: {invoice_id} | Existing #: {existing_partial.invoice_id}")
            print(f"   Existing DB ID: {existing_partial.id}")
            print(f"   ⏭️  Skipping creation to prevent duplicate")
            return existing_partial
    
    # Create invoice with extracted data
    db_invoice = Invoice(
        user_id=user_id,
        # From AI extraction
        invoice_id=extraction_result.invoice_id if extraction_result else invoice_data.invoice_id,
        vendor_name=extraction_result.vendor_name if extraction_result else invoice_data.vendor_name,
        amount_due=extraction_result.amount_due if extraction_result else invoice_data.amount_due,
        due_date=extraction_result.due_date if extraction_result else invoice_data.due_date,
        invoice_date=extraction_result.invoice_date if extraction_result else invoice_data.invoice_date,
        currency_code=extraction_result.currency_code if extraction_result else invoice_data.currency_code,
        confidence_score=extraction_result.confidence_score if extraction_result else 0.0,
        # File metadata
        original_filename=invoice_data.original_filename,
        file_size=invoice_data.file_size,
        file_type=invoice_data.file_type,
        # Processing data
        status=InvoiceStatus.COMPLETED if extraction_result else InvoiceStatus.PENDING,
        extracted_text=extracted_text,
        processed_at=datetime.utcnow() if extraction_result else None,
        # Notes
        notes=invoice_data.notes
    )
    
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    
    print(f"--- ✅ Created invoice {db_invoice.id} for user {user_id} ---")
    return db_invoice


def get_invoice(db: Session, invoice_id: str, user_id: str) -> Optional[Invoice]:
    """
    Get a single invoice by ID (must belong to the user)
    
    Args:
        db: Database session
        invoice_id: Invoice ID
        user_id: User ID (for authorization)
    
    Returns:
        Invoice or None if not found
    """
    return db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.user_id == user_id
    ).first()


def get_invoices(
    db: Session,
    user_id: str,
    skip: int = 0,
    limit: int = 10,
    status: Optional[InvoiceStatus] = None,
    vendor_name: Optional[str] = None
) -> tuple[List[Invoice], int]:
    """
    Get paginated list of invoices for a user
    
    Args:
        db: Database session
        user_id: User ID
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        status: Filter by status (optional)
        vendor_name: Filter by vendor name (optional)
    
    Returns:
        Tuple of (invoices list, total count)
    """
    
    query = db.query(Invoice).filter(Invoice.user_id == user_id)
    
    # Apply filters
    if status:
        query = query.filter(Invoice.status == status)
    if vendor_name:
        query = query.filter(Invoice.vendor_name.ilike(f"%{vendor_name}%"))
    
    # Get total count
    total = query.count()
    
    # Get paginated results (newest first)
    invoices = query.order_by(desc(Invoice.created_at)).offset(skip).limit(limit).all()
    
    return invoices, total


def update_invoice(
    db: Session,
    invoice_id: str,
    user_id: str,
    invoice_update: InvoiceUpdate
) -> Optional[Invoice]:
    """
    Update an invoice
    
    Args:
        db: Database session
        invoice_id: Invoice ID
        user_id: User ID (for authorization)
        invoice_update: Fields to update
    
    Returns:
        Updated Invoice or None if not found
    """
    
    db_invoice = get_invoice(db, invoice_id, user_id)
    
    if not db_invoice:
        return None
    
    # Update fields
    update_data = invoice_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_invoice, field, value)
    
    db_invoice.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_invoice)
    
    print(f"--- ✅ Updated invoice {invoice_id} ---")
    return db_invoice


def delete_invoice(db: Session, invoice_id: str, user_id: str) -> bool:
    """
    Delete an invoice
    
    Args:
        db: Database session
        invoice_id: Invoice ID
        user_id: User ID (for authorization)
    
    Returns:
        True if deleted, False if not found
    """
    
    db_invoice = get_invoice(db, invoice_id, user_id)
    
    if not db_invoice:
        return False
    
    db.delete(db_invoice)
    db.commit()
    
    print(f"--- ✅ Deleted invoice {invoice_id} ---")
    return True


def mark_invoice_failed(
    db: Session,
    invoice_id: str,
    error_message: str
) -> Optional[Invoice]:
    """
    Mark an invoice as failed during processing
    
    Args:
        db: Database session
        invoice_id: Invoice ID
        error_message: Error description
    
    Returns:
        Updated Invoice or None if not found
    """
    
    db_invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    
    if not db_invoice:
        return None
    
    db_invoice.status = InvoiceStatus.FAILED
    db_invoice.processing_error = error_message
    db_invoice.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_invoice)
    
    print(f"--- ⚠️ Marked invoice {invoice_id} as failed: {error_message} ---")
    return db_invoice


def get_invoice_stats(db: Session, user_id: str) -> dict:
    """
    Get statistics about user's invoices
    
    Args:
        db: Database session
        user_id: User ID
    
    Returns:
        Dictionary with statistics
    """
    
    total = db.query(Invoice).filter(Invoice.user_id == user_id).count()
    
    # Count invoices that need review (pending or processing)
    pending = db.query(Invoice).filter(
        Invoice.user_id == user_id,
        Invoice.status.in_([InvoiceStatus.PENDING, InvoiceStatus.PROCESSING])
    ).count()
    
    # Completed invoices are ready for payment
    completed = db.query(Invoice).filter(
        Invoice.user_id == user_id,
        Invoice.status == InvoiceStatus.COMPLETED
    ).count()
    
    # Failed invoices need attention
    failed = db.query(Invoice).filter(
        Invoice.user_id == user_id,
        Invoice.status == InvoiceStatus.FAILED
    ).count()
    
    # Calculate total amount from completed invoices only
    total_amount = db.query(Invoice).filter(
        Invoice.user_id == user_id,
        Invoice.status == InvoiceStatus.COMPLETED,
        Invoice.amount_due.isnot(None)
    ).with_entities(Invoice.amount_due).all()
    
    total_value = sum(amount[0] for amount in total_amount if amount[0])
    
    return {
        "total_invoices": total,
        "pending": pending,  # Includes both pending and processing
        "completed": completed,
        "failed": failed,
        "total_value": round(total_value, 2)
    }
