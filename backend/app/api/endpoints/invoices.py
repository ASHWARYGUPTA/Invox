# /backend/app/api/endpoints/invoices.py
import fitz  # PyMuPDF
import io
from PIL import Image
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

# Import all our new helpers
from app.api import deps
from app.models.user import User
from app.schemas.invoice import InvoiceCreate, Invoice
from app.crud import invoice as crud_invoice

# Import our old Gemini logic (we'll move this to /services/ soon)
from app.services.processing_service import get_invoice_data_from_text, get_invoice_data_from_images, extract_text_from_pdf, convert_pdf_to_images

router = APIRouter()

@router.post("/upload_pdf", response_model=Invoice)
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user) # This line makes the endpoint secure!
):
    """
    "Smart" PDF processor for the logged-in user.
    It links the processed invoice to the user's ID.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")
        
    file_contents = await file.read()
    
    # 1. Try to extract text
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
    
    # 2. Create the InvoiceCreate schema
    invoice_to_create = InvoiceCreate(
        file_name=file.filename,
        **invoice_data.model_dump() # Use model_dump()
    )
    
    # 3. Save to database, linked to the user
    return crud_invoice.create_invoice(db=db, invoice=invoice_to_create, owner_id=current_user.id)

@router.get("/my_invoices", response_model=List[Invoice])
def get_my_invoices(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user) # Secure endpoint
):
    """
    Gets a list of all invoices uploaded by the current user.
    """
    return crud_invoice.get_invoices_by_owner(db=db, owner_id=current_user.id)