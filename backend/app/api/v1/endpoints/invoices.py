"""
Invoice API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import csv
import json
import io
from app.db.session import get_db
from app.api.deps import get_current_active_user
from app.models.user import User as UserModel
from app.models.invoice import InvoiceStatus
from app.schemas.invoice import (
    Invoice,
    InvoiceList,
    InvoiceUpdate,
    InvoiceUploadResponse,
    InvoiceCreate
)
from app.crud import invoice as invoice_crud
from app.services.invoice_processing import process_invoice_file, extract_text_from_pdf

router = APIRouter()


@router.post("/upload", response_model=InvoiceUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_invoice(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Upload and process an invoice file (PDF, JPG, PNG)
    
    - Extracts invoice data using Google Gemini AI
    - Stores invoice in database
    - Returns extracted information
    """
    
    # Validate file type
    allowed_types = ["application/pdf", "image/jpeg", "image/jpg", "image/png"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file.content_type} not supported. Please upload PDF, JPG, or PNG."
        )
    
    # Validate file size (max 10MB)
    file_contents = await file.read()
    file_size = len(file_contents)
    max_size = 10 * 1024 * 1024  # 10MB
    
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size ({file_size / (1024*1024):.2f}MB) exceeds maximum allowed size (10MB)"
        )
    
    print(f"--- 📤 Processing upload: {file.filename} ({file.content_type}, {file_size} bytes) ---")
    
    try:
        # Process the invoice file with Gemini AI
        extraction_result = process_invoice_file(file_contents, file.content_type)
        
        # Extract text if PDF (for search/reference)
        extracted_text = None
        if file.content_type == "application/pdf":
            extracted_text = extract_text_from_pdf(file_contents)
        
        # Determine file type
        file_type = "pdf" if file.content_type == "application/pdf" else file.content_type.split("/")[1]
        
        # Create invoice in database
        invoice_data = InvoiceCreate(
            original_filename=file.filename,
            file_size=file_size,
            file_type=file_type
        )
        
        db_invoice = invoice_crud.create_invoice(
            db=db,
            user_id=current_user.id,  # type: ignore
            invoice_data=invoice_data,
            extraction_result=extraction_result,
            extracted_text=extracted_text
        )
        
        return InvoiceUploadResponse(
            message="Invoice uploaded and processed successfully",
            invoice=Invoice.model_validate(db_invoice),
            extraction_data=extraction_result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"--- ❌ Error processing invoice: {e} ---")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing invoice: {str(e)}"
        )


@router.get("/", response_model=InvoiceList)
def list_invoices(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    status_filter: Optional[InvoiceStatus] = Query(None, description="Filter by status"),
    vendor_name: Optional[str] = Query(None, description="Filter by vendor name"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Get paginated list of user's invoices
    
    - Supports filtering by status and vendor name
    - Sorted by creation date (newest first)
    """
    
    skip = (page - 1) * page_size
    
    invoices, total = invoice_crud.get_invoices(
        db=db,
        user_id=current_user.id,  # type: ignore
        skip=skip,
        limit=page_size,
        status=status_filter,
        vendor_name=vendor_name
    )
    
    return InvoiceList(
        total=total,
        invoices=[Invoice.model_validate(inv) for inv in invoices],
        page=page,
        page_size=page_size
    )


@router.get("/stats")
def get_invoice_statistics(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Get statistics about user's invoices
    
    - Total count
    - Count by status
    - Total value
    """
    
    stats = invoice_crud.get_invoice_stats(
        db=db,
        user_id=current_user.id  # type: ignore
    )
    
    return stats


@router.get("/export")
async def export_invoices(
    format: str = Query("csv", description="Export format: csv or json"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    start_date: Optional[str] = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter by end date (YYYY-MM-DD)"),
    min_amount: Optional[float] = Query(None, description="Minimum invoice amount"),
    max_amount: Optional[float] = Query(None, description="Maximum invoice amount"),
    vendor_name: Optional[str] = Query(None, description="Filter by vendor name"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Export invoices to CSV or JSON format with optional filters
    """
    
    # Build filters
    filters = {}
    if status_filter:
        try:
            filters['status'] = InvoiceStatus(status_filter)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status: {status_filter}"
            )
    
    if vendor_name:
        filters['vendor_name'] = vendor_name
    
    # Get invoices (without pagination for export)
    invoices, _ = invoice_crud.get_invoices(
        db=db,
        user_id=current_user.id,  # type: ignore
        skip=0,
        limit=10000,  # Large limit for export
        status=filters.get('status'),
        vendor_name=filters.get('vendor_name')
    )
    
    # Apply additional filters
    filtered_invoices = []
    for invoice in invoices:
        # Date range filter (invoice_date is stored as string in YYYY-MM-DD format)
        if start_date and invoice.invoice_date:
            try:
                if invoice.invoice_date < start_date:
                    continue
            except (ValueError, TypeError):
                pass
        
        if end_date and invoice.invoice_date:
            try:
                if invoice.invoice_date > end_date:
                    continue
            except (ValueError, TypeError):
                pass
        
        # Amount range filter (amount_due is the field name)
        if min_amount is not None and invoice.amount_due is not None:
            if invoice.amount_due < min_amount:
                continue
        
        if max_amount is not None and invoice.amount_due is not None:
            if invoice.amount_due > max_amount:
                continue
        
        filtered_invoices.append(invoice)
    
    # Generate export based on format
    if format.lower() == "json":
        # JSON export
        invoice_list = []
        for inv in filtered_invoices:
            invoice_dict = {
                "id": inv.id,
                "invoice_number": inv.invoice_id or "",  # invoice_id is the field name in DB
                "vendor_name": inv.vendor_name or "",
                "invoice_date": inv.invoice_date or "",  # Already stored as string
                "due_date": inv.due_date or "",  # Already stored as string
                "total_amount": float(inv.amount_due) if inv.amount_due else None,  # amount_due is the field name
                "currency": inv.currency_code or "",  # currency_code is the field name
                "status": inv.status.value if inv.status else "",
                "original_filename": inv.original_filename or "",
                "created_at": inv.created_at.isoformat() if inv.created_at else "",
                "notes": inv.notes or ""
            }
            invoice_list.append(invoice_dict)
        
        json_str = json.dumps(invoice_list, indent=2)
        
        return StreamingResponse(
            io.BytesIO(json_str.encode()),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=invoices_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            }
        )
    
    else:
        # CSV export (default)
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "ID",
            "Invoice Number",
            "Vendor Name",
            "Invoice Date",
            "Due Date",
            "Total Amount",
            "Currency",
            "Status",
            "Original Filename",
            "Created At",
            "Notes"
        ])
        
        # Write data
        for inv in filtered_invoices:
            writer.writerow([
                inv.id,
                inv.invoice_id or "",  # invoice_id is the field name in DB
                inv.vendor_name or "",
                inv.invoice_date or "",  # Already stored as string
                inv.due_date or "",  # Already stored as string
                inv.amount_due or "",  # amount_due is the field name
                inv.currency_code or "",  # currency_code is the field name
                inv.status.value if inv.status else "",
                inv.original_filename or "",
                inv.created_at.isoformat() if inv.created_at else "",
                inv.notes or ""
            ])
        
        output.seek(0)
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=invoices_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        )


@router.get("/{invoice_id}", response_model=Invoice)
def get_invoice(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Get a specific invoice by ID
    """
    
    db_invoice = invoice_crud.get_invoice(
        db=db,
        invoice_id=invoice_id,
        user_id=current_user.id  # type: ignore
    )
    
    if not db_invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    return Invoice.model_validate(db_invoice)


@router.put("/{invoice_id}", response_model=Invoice)
def update_invoice(
    invoice_id: str,
    invoice_update: InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Update invoice information
    
    - Can update extracted fields if AI made mistakes
    - Can add notes
    - Can change status
    """
    
    db_invoice = invoice_crud.update_invoice(
        db=db,
        invoice_id=invoice_id,
        user_id=current_user.id,  # type: ignore
        invoice_update=invoice_update
    )
    
    if not db_invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    return Invoice.model_validate(db_invoice)


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Delete an invoice
    """
    
    success = invoice_crud.delete_invoice(
        db=db,
        invoice_id=invoice_id,
        user_id=current_user.id  # type: ignore
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    return None
