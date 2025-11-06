# /backend/app/api/endpoints/invoices.py
import fitz  # PyMuPDF
import io
import csv
import json
from datetime import datetime
from io import StringIO
from PIL import Image
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

# Import all our new helpers
from app.api import deps
from app.models.user import User
from app.schemas.invoice import InvoiceCreate, Invoice, InvoiceUpdate
from app.crud import invoice as crud_invoice

# Import our old Gemini logic (we'll move this to /services/ soon)
from app.services.processing_service import get_invoice_data_from_text, get_invoice_data_from_images, extract_text_from_pdf, convert_pdf_to_images
from app.services.canonicalization import canonicalize_invoice_data, validate_canonicalized_data

router = APIRouter()

@router.post("/upload_pdf", response_model=Invoice)
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user) # This line makes the endpoint secure!
):
    """
    "Smart" invoice processor for the logged-in user.
    Accepts PDFs and images (PNG, JPG, JPEG).
    It links the processed invoice to the user's ID.
    """
    print(f"📄 Upload request from user {current_user.id} ({current_user.email})")
    print(f"   File: {file.filename}")
    print(f"   Content-Type: {file.content_type}")
    
    # Accept PDF and common image types
    allowed_types = ["application/pdf", "image/png", "image/jpeg", "image/jpg"]
    
    if file.content_type not in allowed_types:
        print(f"   ❌ Invalid file type: {file.content_type}")
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type '{file.content_type}'. Please upload a PDF or image (PNG, JPG, JPEG)."
        )
        
    file_contents = await file.read()
    print(f"   File size: {len(file_contents)} bytes")
    
    try:
        # Handle based on file type
        if file.content_type == "application/pdf":
            # 1. Try to extract text from PDF
            extracted_text = extract_text_from_pdf(file_contents)
            
            if extracted_text and len(extracted_text) > 100:
                print("--- 🧠 PDF is text-based. Using text extraction. ---")
                invoice_data = get_invoice_data_from_text(extracted_text)
            else:
                print("--- 🧠 PDF is scanned. Using image conversion. ---")
                images = convert_pdf_to_images(file_contents)
                if not images:
                    raise HTTPException(status_code=400, detail="PDF is empty or could not be processed.")
                invoice_data = get_invoice_data_from_images(images)
        
        else:
            # Handle image files directly
            print("--- 🖼️ Processing image file. ---")
            from PIL import Image
            import io
            image = Image.open(io.BytesIO(file_contents))
            invoice_data = get_invoice_data_from_images([image])
        
        # Validate that we extracted meaningful invoice data
        has_meaningful_data = (
            invoice_data.invoice_id is not None or 
            (invoice_data.vendor_name is not None and invoice_data.amount_due is not None)
        )
        
        if not has_meaningful_data:
            print(f"   ❌ No meaningful invoice data extracted from {file.filename}")
            raise HTTPException(
                status_code=400, 
                detail="Could not extract invoice data. The file doesn't appear to contain a valid invoice."
            )
        
        # 2. Apply canonicalization to normalize data
        print("   📏 Applying data canonicalization...")
        canonicalized = canonicalize_invoice_data(
            invoice_id=invoice_data.invoice_id,
            vendor_name=invoice_data.vendor_name,
            amount_due=invoice_data.amount_due,
            due_date=invoice_data.due_date,
            invoice_date=invoice_data.invoice_date,
            currency_code=invoice_data.currency_code,
            confidence_score=invoice_data.confidence_score
        )
        
        # Validate canonicalized data
        is_valid, error_msg = validate_canonicalized_data(canonicalized)
        if not is_valid:
            print(f"   ❌ Validation failed: {error_msg}")
            raise HTTPException(status_code=400, detail=f"Data validation failed: {error_msg}")
        
        # 3. Create the InvoiceCreate schema with canonicalized data
        invoice_to_create = InvoiceCreate(
            file_name=file.filename,
            invoice_id=canonicalized["invoice_id"],
            vendor_name=canonicalized["vendor_name"],
            amount_due=canonicalized["amount_due"],
            due_date=canonicalized["due_date"],
            invoice_date=canonicalized["invoice_date"],
            currency_code=canonicalized["currency_code"],
            confidence_score=canonicalized["confidence_score"]
        )
        
        # Set the status based on confidence
        if invoice_to_create.confidence_score and invoice_to_create.confidence_score >= 0.90:
            invoice_to_create.status = "approved"
        else:
            invoice_to_create.status = "needs_review"

        # 3. Save to database, linked to the user
        created_invoice, is_duplicate = crud_invoice.create_invoice(db=db, invoice=invoice_to_create, owner_id=current_user.id)
        
        if is_duplicate:
            print(f"   ⚠️  Duplicate invoice detected, returning existing invoice ID {created_invoice.id}")
        else:
            print(f"   ✅ Successfully saved invoice ID {created_invoice.id} for user {current_user.email}")
        
        return created_invoice
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"   ❌ Error processing PDF: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
    
@router.get("/my_invoices", response_model=List[Invoice])
def get_my_invoices(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user) # Secure endpoint
):
    """
    Gets a list of all invoices uploaded by the current user.
    """
    return crud_invoice.get_invoices_by_owner(db=db, owner_id=current_user.id)

@router.put("/{invoice_id}", response_model=Invoice)
def update_invoice_data(
    invoice_id: int,
    invoice_in: InvoiceUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Update an invoice's details (for HITL).
    """
    # First, get the invoice from the DB
    db_invoice = crud_invoice.get_invoice_by_id(db, invoice_id=invoice_id) # We need to create this CRUD function
    
    if not db_invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    # Check if the user owns this invoice
    if db_invoice.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this invoice")
        
    # Update the status to 'approved' if it's being reviewed
    if invoice_in.status is None:
        invoice_in.status = "approved"
        
    # Update the invoice
    updated_invoice = crud_invoice.update_invoice(db=db, db_invoice=db_invoice, invoice_in=invoice_in)
    return updated_invoice

@router.get("/export")
async def export_invoices(
    format: str = Query(..., description="Export format: 'csv' or 'json'"),
    status: Optional[str] = Query(None, description="Filter by status: 'approved', 'needs_review', or None for all"),
    start_date: Optional[str] = Query(None, description="Filter by invoice date >= start_date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter by invoice date <= end_date (YYYY-MM-DD)"),
    min_amount: Optional[float] = Query(None, description="Filter by amount >= min_amount"),
    max_amount: Optional[float] = Query(None, description="Filter by amount <= max_amount"),
    vendor_name: Optional[str] = Query(None, description="Filter by vendor name (partial match)"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Export user's invoices as CSV or JSON with optional filters.
    
    Filters:
    - status: approved, needs_review, or all
    - start_date/end_date: Date range filter
    - min_amount/max_amount: Amount range filter
    - vendor_name: Search by vendor name
    """
    
    # Validate format
    if format.lower() not in ['csv', 'json']:
        raise HTTPException(status_code=400, detail="Format must be 'csv' or 'json'")
    
    # Get all user's invoices
    invoices = crud_invoice.get_invoices_by_owner(db=db, owner_id=current_user.id)
    
    # Apply filters
    filtered_invoices = []
    for invoice in invoices:
        # Status filter
        if status and invoice.status != status:
            continue
            
        # Date range filter
        if start_date and invoice.invoice_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d").date()
                inv_date = datetime.strptime(invoice.invoice_date, "%Y-%m-%d").date() if isinstance(invoice.invoice_date, str) else invoice.invoice_date
                if inv_date < start:
                    continue
            except ValueError:
                pass
                
        if end_date and invoice.invoice_date:
            try:
                end = datetime.strptime(end_date, "%Y-%m-%d").date()
                inv_date = datetime.strptime(invoice.invoice_date, "%Y-%m-%d").date() if isinstance(invoice.invoice_date, str) else invoice.invoice_date
                if inv_date > end:
                    continue
            except ValueError:
                pass
        
        # Amount range filter
        if min_amount is not None and invoice.amount_due is not None:
            if invoice.amount_due < min_amount:
                continue
                
        if max_amount is not None and invoice.amount_due is not None:
            if invoice.amount_due > max_amount:
                continue
        
        # Vendor name filter
        if vendor_name and invoice.vendor_name:
            if vendor_name.lower() not in invoice.vendor_name.lower():
                continue
        
        filtered_invoices.append(invoice)
    
    # Export as CSV
    if format.lower() == 'csv':
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Invoice ID', 'Vendor Name', 'Amount Due', 'Currency', 
            'Invoice Date', 'Due Date', 'Status', 'Confidence Score',
            'File Name', 'Created At'
        ])
        
        # Write data
        for invoice in filtered_invoices:
            writer.writerow([
                invoice.invoice_id or 'N/A',
                invoice.vendor_name or 'N/A',
                invoice.amount_due or 0,
                invoice.currency_code or 'USD',
                invoice.invoice_date or 'N/A',
                invoice.due_date or 'N/A',
                invoice.status,
                f"{invoice.confidence_score * 100:.1f}%" if invoice.confidence_score else 'N/A',
                invoice.file_name,
                invoice.created_at.strftime("%Y-%m-%d %H:%M:%S") if invoice.created_at else 'N/A'
            ])
        
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=invoices_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        )
    
    # Export as JSON
    else:
        invoice_list = []
        for invoice in filtered_invoices:
            invoice_list.append({
                'id': invoice.id,
                'invoice_id': invoice.invoice_id,
                'vendor_name': invoice.vendor_name,
                'amount_due': float(invoice.amount_due) if invoice.amount_due else None,
                'currency_code': invoice.currency_code,
                'invoice_date': invoice.invoice_date,
                'due_date': invoice.due_date,
                'status': invoice.status,
                'confidence_score': float(invoice.confidence_score) if invoice.confidence_score else None,
                'file_name': invoice.file_name,
                'created_at': invoice.created_at.isoformat() if invoice.created_at else None,
                'updated_at': invoice.updated_at.isoformat() if invoice.updated_at else None
            })
        
        json_data = json.dumps(invoice_list, indent=2)
        return StreamingResponse(
            iter([json_data]),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=invoices_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            }
        )

@router.post("/poll-emails")
async def poll_emails(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Manually trigger email polling to check for new invoices.
    This can be called from the frontend to check emails on-demand.
    
    Requires Gmail API authentication to be set up first.
    See backend/app/worker/GMAIL_SETUP.md for setup instructions.
    """
    try:
        # Import the email polling logic
        from app.worker.email_poller import get_gmail_service, check_for_invoices
        
        # Get Gmail service (this handles authentication)
        service = get_gmail_service()
        if not service:
            raise HTTPException(
                status_code=500, 
                detail="Failed to connect to Gmail service. Please run the authentication setup script."
            )
        
        # Check for invoices (limit to 5 most recent emails)
        invoices_processed = check_for_invoices(service, db, max_emails=5)
        
        return {
            "success": True,
            "message": f"Email polling completed. {invoices_processed} new invoice(s) processed.",
            "invoices_count": invoices_processed
        }
    except FileNotFoundError as e:
        # Credentials file not found
        print(f"Credentials file not found: {e}")
        raise HTTPException(
            status_code=500,
            detail="Gmail API credentials not configured. Please set up credentials.json in backend/app/worker/"
        )
    except ValueError as e:
        # Token file issues (missing refresh_token, etc.)
        error_msg = str(e)
        print(f"Gmail authentication error: {error_msg}")
        
        if "refresh_token" in error_msg.lower():
            raise HTTPException(
                status_code=500,
                detail="Gmail authentication token is invalid. Please run: python backend/app/worker/authenticate_gmail.py"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Gmail authentication error: {error_msg}"
            )
    except Exception as e:
        print(f"Error during manual email polling: {e}")
        import traceback
        traceback.print_exc()
        
        # Provide more helpful error messages
        error_msg = str(e)
        if "credentials" in error_msg.lower():
            detail = "Gmail API authentication failed. Please run the authentication setup script."
        elif "token" in error_msg.lower():
            detail = "Gmail API token error. Please re-authenticate using: python backend/app/worker/authenticate_gmail.py"
        else:
            detail = f"Failed to poll emails: {error_msg}"
        
        raise HTTPException(
            status_code=500,
            detail=detail
        )
