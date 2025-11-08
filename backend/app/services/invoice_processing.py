"""
Invoice processing service using Google Gemini AI
EXACT COPY of logic from backend/app/services/processing_service.py
"""
import os
import json
from google import genai
import fitz  # PyMuPDF
from PIL import Image
from fastapi import HTTPException
from typing import List
from app.schemas.invoice import InvoiceExtractionResponse
from app.core.config import settings


# --- Setup Gemini Client ---
try:
    # Get API key from settings
    api_key = settings.GOOGLE_API_KEY if hasattr(settings, 'GOOGLE_API_KEY') else os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("❌ CRITICAL: GOOGLE_API_KEY not found in environment variables!")
        print("Please add GOOGLE_API_KEY to your .env file")
        client = None
    else:
        print(f"✅ Found GOOGLE_API_KEY: {api_key[:10]}...")
        client = genai.Client(api_key=api_key)
        print("--- 🤖 Gemini Client Initialized (Invoice Processing Service) ---")
except Exception as e:
    print(f"CRITICAL: Error configuring Gemini API: {e}")
    client = None


# --- Prompts (EXACT COPY from processing_service.py) ---
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


# --- Generation Configuration ---
generation_config = {
    "temperature": 0.0,
    "response_mime_type": "application/json",
}


# --- Core AI Functions (EXACT COPY) ---

def get_invoice_data_from_text(text: str) -> InvoiceExtractionResponse:
    """
    Sends text to Gemini and returns validated Pydantic model.
    EXACT COPY from processing_service.py
    """
    
    # Check if client is initialized
    if client is None:
        raise HTTPException(
            status_code=500,
            detail="Gemini API client not initialized. Please check your GOOGLE_API_KEY."
        )
    
    final_prompt = TEXT_PROMPT_TEMPLATE.format(invoice_text=text)
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
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
        
        # Remove double curly braces if present (Gemini sometimes adds them)
        if json_output.startswith("{{") and json_output.endswith("}}"):
            json_output = json_output[1:-1].strip()
            print(f"--- 🔧 Removed double curly braces, cleaned output: {json_output} ---")
        
        data = json.loads(json_output)
        validated_data = InvoiceExtractionResponse(**data)
        
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


def get_invoice_data_from_images(images: List[Image.Image]) -> InvoiceExtractionResponse:
    """
    Sends images to Gemini (multimodal) and returns validated data.
    EXACT COPY from processing_service.py
    """
    
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
            model="gemini-2.0-flash-exp",
            contents=content,
            config=generation_config
        )
        
        # Debug: Print the raw response
        print(f"--- 🔍 Raw Gemini Response (IMAGE): {response} ---")
        print(f"--- 🔍 Response Text (IMAGE): {response.text} ---")
        
        json_output = response.text.strip()
        
        # Check if response is empty
        if not json_output:
            raise ValueError("Gemini returned an empty response")
        
        # Remove double curly braces if present (Gemini sometimes adds them)
        if json_output.startswith("{{") and json_output.endswith("}}"):
            json_output = json_output[1:-1].strip()
            print(f"--- 🔧 Removed double curly braces, cleaned output: {json_output} ---")
        
        data = json.loads(json_output)
        validated_data = InvoiceExtractionResponse(**data)
        
        print("--- ✅ Successfully processed IMAGE(S) ---")
        return validated_data

    except json.JSONDecodeError as e:
        print(f"--- ❌ JSON Decode Error (IMAGE): {e} ---")
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


# --- Helper Functions (EXACT COPY) ---

def extract_text_from_pdf(file_contents: bytes) -> str:
    """
    Extract text from PDF file.
    EXACT COPY from processing_service.py
    """
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
    if all_text:
        print(f"--- 📝 Text preview: {all_text[:200]}... ---")
    return all_text


def convert_pdf_to_images(file_contents: bytes) -> List[Image.Image]:
    """
    Convert PDF pages to images for OCR.
    EXACT COPY from processing_service.py
    """
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


def convert_image_file(file_contents: bytes, content_type: str) -> Image.Image:
    """
    Convert uploaded image file to PIL Image
    """
    try:
        from io import BytesIO
        img = Image.open(BytesIO(file_contents))
        print(f"--- 🖼️ Loaded image: {img.format} {img.size} ---")
        return img
    except Exception as e:
        print(f"--- ❌ Error loading image: {e} ---")
        raise HTTPException(
            status_code=400,
            detail=f"Error processing image file: {e}"
        )


def process_invoice_file(file_contents: bytes, content_type: str) -> InvoiceExtractionResponse:
    """
    Main function to process any invoice file (PDF or image).
    Automatically detects file type and uses appropriate extraction method.
    
    Args:
        file_contents: Raw file bytes
        content_type: MIME type of the file
    
    Returns:
        InvoiceExtractionResponse with extracted data
    """
    
    print(f"--- 🚀 Processing invoice file: {content_type} ---")
    
    # Handle PDF files
    if content_type == "application/pdf" or content_type.endswith("/pdf"):
        # Try text extraction first
        text = extract_text_from_pdf(file_contents)
        
        if text and len(text.strip()) > 50:  # If we got meaningful text
            print("--- 📄 Using text extraction method ---")
            return get_invoice_data_from_text(text)
        else:
            # Fall back to image-based extraction for scanned PDFs
            print("--- 🖼️ PDF has no text, using image extraction ---")
            images = convert_pdf_to_images(file_contents)
            return get_invoice_data_from_images(images)
    
    # Handle image files (jpg, png, etc.)
    elif content_type.startswith("image/"):
        print("--- 🖼️ Using image extraction method ---")
        img = convert_image_file(file_contents, content_type)
        return get_invoice_data_from_images([img])
    
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {content_type}. Please upload PDF, JPG, or PNG files."
        )
