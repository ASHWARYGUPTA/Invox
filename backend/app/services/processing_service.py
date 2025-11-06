# /backend/app/services/processing_service.py

import os
import json
from google import genai
import fitz  # PyMuPDF
import io
from PIL import Image
from fastapi import HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

# --- 1. Pydantic Model (Copied from main.py) ---
# We need this here for the function return types
class InvoiceResponse(BaseModel):
    invoice_id: Optional[str]
    vendor_name: Optional[str]
    amount_due: Optional[float]
    due_date: Optional[str]
    confidence_score: float = Field(..., ge=0.0, le=1.0)

# --- 2. Setup (Copied from main.py) ---
try:
    client = genai.Client()
    print("--- 🤖 Gemini Client Initialized (from processing_service) ---")
except Exception as e:
    print(f"CRITICAL: Error configuring API key: {e}")

# --- 3. Prompts (Copied from main.py) ---
BASE_PROMPT = """
            "You are an expert at understanding invoices and billing documents. "
            "Extract the following fields if present and return ONLY valid JSON (no prose):\n"
            "{\n"
            "  "invoiceNumber": string|null,\n"
            "  "invoiceDate": string|null,  // ISO date if possible\n"
            "  "dueDate": string|null,      // ISO date if possible\n"
            "  "amountPayable": number|null,\n"
            "  "currency": string|null,\n"
            "  "vendorName": string|null,\n"
            "  "customerName": string|null,\n"
            "  "poNumber": string|null,\n"
            "  "ConfidenceScore": number|null, -> It represents how confidentent Gemini Percentage is with this post\n"
            "  "lineItems": [ { "description": string, "quantity": number|null, "unitPrice": number|null, "total": number|null } ]\n"
            "}\n"
            "Be concise. If a field is not found, set it to null."
        

Rules:
- If a field is not present, its value must be null.
- `vendor_name` should be the name of the company sending the invoice.
- `amount_due` should be the final total amount.
- `confidence_score` should be your best estimate of the accuracy.
"""

TEXT_PROMPT_TEMPLATE = BASE_PROMPT + """

Here is the invoice text:
---
{invoice_text}
---
"""

IMAGE_PROMPT_TEMPLATE = BASE_PROMPT + """

Here is the invoice (as one or more images). Extract the data from them.
"""

# --- 4. AI Logic (Copied from main.py) ---

generation_config = {
    "temperature": 0.0,
    "response_mime_type": "application/json",
}

# ⬇️⬇️⬇️ THIS IS THE LOGIC WE MOVED ⬇️⬇️⬇️

def get_invoice_data_from_text(text: str) -> InvoiceResponse:
    """Sends text to Gemini and returns validated Pydantic model."""
    
    final_prompt = TEXT_PROMPT_TEMPLATE.format(invoice_text=text)
    
    try:
        response = client.models.generate_content(
            model="models/gemini-2.5-flash", 
            contents=[final_prompt]
        )
        json_output = response.text.strip()
        data = json.loads(json_output)
        validated_data = InvoiceResponse(**data)
        
        print("--- ✅ Successfully processed TEXT ---")
        return validated_data

    except Exception as e:
        print(f"--- ❌ An error occurred during TEXT processing: {e} ---")
        raise HTTPException(
            status_code=500, 
            detail=f"An internal error occurred: {e}"
        )

def get_invoice_data_from_images(images: List[Image.Image]) -> InvoiceResponse:
    """Sends images to Gemini (multimodal) and returns validated data."""
    
    content = [IMAGE_PROMPT_TEMPLATE]
    content.extend(images)
    
    try:
        response = client.models.generate_content(
            model="models/gemini-2.5-flash", 
            contents=content
        )
        
        json_output = response.text.strip()
        data = json.loads(json_output)
        validated_data = InvoiceResponse(**data)
        
        print("--- ✅ Successfully processed IMAGE(S) ---")
        return validated_data

    except Exception as e:
        print(f"--- ❌ An error occurred during IMAGE processing: {e} ---")
        raise HTTPException(
            status_code=500, 
            detail=f"An internal error occurred: {e}"
        )

# --- 5. Helper Functions (Copied from main.py) ---

def extract_text_from_pdf(file_contents: bytes) -> str:
    all_text = ""
    try:
        pdf_document = fitz.open(stream=file_contents, filetype="pdf")
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            all_text += page.get_text()
        pdf_document.close()
    except Exception as e:
        print(f"Error extracting PDF text (file might be image-only): {e}")
        return ""
        
    print(f"--- 📄 Extracted {len(all_text)} chars from PDF ---")
    print(all_text)
    return all_text

def convert_pdf_to_images(file_contents: bytes) -> List[Image.Image]:
    images = []
    try:
        pdf_document = fitz.open(stream=file_contents, filetype="pdf")
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            pix = page.get_pixmap(dpi=200)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(img)
        pdf_document.close()
        
        print(f"--- 🖼️ Converted PDF to {len(images)} image(s) ---")
        return images
        
    except Exception as e:
        print(f"--- ❌ Error converting PDF to images: {e} ---")
        raise HTTPException(
            status_code=400,
            detail=f"Error processing PDF file for scanning: {e}"
        )