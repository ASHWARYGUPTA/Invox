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
    invoice_id: Optional[str] = None
    vendor_name: Optional[str] = None
    amount_due: Optional[float] = None
    due_date: Optional[str] = None
    invoice_date: Optional[str] = None
    currency_code: Optional[str] = "USD"
    confidence_score: float = 0.0  # Default to 0.0 if not provided

# --- 2. Setup (Copied from main.py) ---
try:
    # Check if API key is set
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ CRITICAL: GOOGLE_API_KEY not found in environment variables!")
        print("Please check your .env file")
    else:
        print(f"✅ Found GOOGLE_API_KEY: {api_key[:10]}...")
    
    client = genai.Client(api_key=api_key)
    print("--- 🤖 Gemini Client Initialized (from processing_service) ---")
except Exception as e:
    print(f"CRITICAL: Error configuring API key: {e}")
    client = None

# --- 3. Prompts (Copied from main.py) ---
BASE_PROMPT = """
You are an expert at understanding invoices and billing documents.
Extract the following fields if present and return ONLY valid JSON (no prose):

IMPORTANT: Use these EXACT field names (snake_case):
{{
  "invoice_id": string|null,
  "vendor_name": string|null,
  "amount_due": number|null,
  "due_date": string (YYYY-MM-DD format)|null,
  "invoice_date": string (YYYY-MM-DD format)|null,
  "currency_code": string (ISO 4217: USD, INR, EUR, GBP, etc.)|null,
  "confidence_score": number (0.0 to 1.0)
}}

Field descriptions:
- invoice_id: The unique invoice or bill number
- vendor_name: The company or person issuing the invoice
- amount_due: The total amount to be paid (numeric value only, no currency symbols)
- due_date: Payment deadline in YYYY-MM-DD format
- invoice_date: Date the invoice was issued in YYYY-MM-DD format
- currency_code: 3-letter ISO currency code (USD, INR, EUR, GBP, CAD, AUD, etc.)
- confidence_score: Your confidence in the extraction (0.0 = no confidence, 1.0 = very confident)

Rules:
- If a field is not found, set it to null
- Return dates in ISO 8601 format (YYYY-MM-DD)
- Return currency as 3-letter uppercase ISO code
- Extract amount as number without currency symbols
- Return ONLY the JSON object, no additional text
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
    
    # Check if client is initialized
    if client is None:
        raise HTTPException(
            status_code=500,
            detail="Gemini API client not initialized. Please check your GOOGLE_API_KEY."
        )
    
    final_prompt = TEXT_PROMPT_TEMPLATE.format(invoice_text=text)
    
    try:
        response = client.models.generate_content(
            model="models/gemini-2.5-flash", 
            contents=[final_prompt],
            config=generation_config
        )
        
        # Debug: Print the raw response
        print(f"--- 🔍 Raw Gemini Response (TEXT): {response} ---")
        print(f"--- 🔍 Response Text (TEXT): {response.text} ---")
        
        json_output = response.text.strip()
        
        # Check if response is empty
        if not json_output:
            raise ValueError("Gemini returned an empty response")
        
        data = json.loads(json_output)
        validated_data = InvoiceResponse(**data)
        
        print("--- ✅ Successfully processed TEXT ---")
        return validated_data

    except json.JSONDecodeError as e:
        print(f"--- ❌ JSON Decode Error (TEXT): {e} ---")
        print(f"--- 🔍 Attempted to parse: {json_output if 'json_output' in locals() else 'No output'} ---")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to parse Gemini response as JSON: {e}"
        )
    except Exception as e:
        print(f"--- ❌ An error occurred during TEXT processing: {e} ---")
        raise HTTPException(
            status_code=500, 
            detail=f"An internal error occurred: {e}"
        )

def get_invoice_data_from_images(images: List[Image.Image]) -> InvoiceResponse:
    """Sends images to Gemini (multimodal) and returns validated data."""
    
    # Check if client is initialized
    if client is None:
        raise HTTPException(
            status_code=500,
            detail="Gemini API client not initialized. Please check your GOOGLE_API_KEY."
        )
    
    content = [IMAGE_PROMPT_TEMPLATE]
    content.extend(images)
    
    try:
        response = client.models.generate_content(
            model="models/gemini-2.5-flash", 
            contents=content,
            config=generation_config
        )
        
        # Debug: Print the raw response
        print(f"--- 🔍 Raw Gemini Response: {response} ---")
        print(f"--- 🔍 Response Text: {response.text} ---")
        
        json_output = response.text.strip()
        
        # Check if response is empty
        if not json_output:
            raise ValueError("Gemini returned an empty response")
        
        data = json.loads(json_output)
        validated_data = InvoiceResponse(**data)
        
        print("--- ✅ Successfully processed IMAGE(S) ---")
        return validated_data

    except json.JSONDecodeError as e:
        print(f"--- ❌ JSON Decode Error: {e} ---")
        print(f"--- 🔍 Attempted to parse: {json_output if 'json_output' in locals() else 'No output'} ---")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to parse Gemini response as JSON: {e}"
        )
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