"""
Invoice processing service using OpenRouter AI
"""
import os
import json
import base64
import time
from io import BytesIO
from openai import OpenAI, RateLimitError, NotFoundError
import fitz  # PyMuPDF
from PIL import Image
from fastapi import HTTPException
from typing import List
from app.schemas.invoice import InvoiceExtractionResponse
from app.core.config import settings


# --- Setup OpenRouter Client ---
try:
    api_key = settings.OPENROUTER_API_KEY if hasattr(settings, 'OPENROUTER_API_KEY') else os.getenv("OPENROUTER_API_KEY")
    model_name = settings.LLM_MODEL or settings.OPENROUTER_MODEL_NAME or "google/gemma-4-26b-a4b-it:free"
    
    if not api_key:
        print("❌ CRITICAL: OPENROUTER_API_KEY not found in environment variables!")
        client = None
    else:
        print(f"✅ Found OPENROUTER_API_KEY: {api_key[:10]}...")
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        print(f"--- 🤖 OpenRouter Client Initialized | Model: {model_name} ---")
except Exception as e:
    print(f"CRITICAL: Error configuring OpenRouter API: {e}")
    client = None
    model_name = "google/gemma-4-26b-a4b-it:free"


def _get_model_chain() -> list:
    """Return [primary_model, *fallbacks] from settings."""
    primary = settings.LLM_MODEL or settings.OPENROUTER_MODEL_NAME or "qwen/qwen3-8b:free"
    fallbacks_str = getattr(settings, 'OPENROUTER_FALLBACK_MODELS', '') or ''
    fallbacks = [m.strip() for m in fallbacks_str.split(',') if m.strip()]
    return [primary] + fallbacks


def _chat_with_retry(messages: list, **kwargs):
    """
    Call OpenRouter with a model fallback chain.
    Falls back to next model on:
      - 429 RateLimitError (rate-limited on shared free pool)
      - 404 NotFoundError  (model removed or :free tier discontinued)
    Raises HTTPException(503) only if ALL models in the chain fail.
    """
    model_chain = _get_model_chain()
    
    for i, model in enumerate(model_chain):
        retries = 2
        for attempt in range(retries):
            try:
                print(f"🤖 Trying model: {model} (attempt {attempt+1}/{retries})")
                return client.chat.completions.create(
                    model=model,
                    messages=messages,
                    **kwargs
                )
            except (RateLimitError, NotFoundError) as e:
                err_type = "rate-limited (429)" if isinstance(e, RateLimitError) else "unavailable/removed (404)"
                wait = 2 ** attempt  # 1s, 2s
                if attempt < retries - 1 and isinstance(e, RateLimitError):
                    print(f"⚠️  {model} {err_type}, retrying in {wait}s...")
                    time.sleep(wait)
                else:
                    if i < len(model_chain) - 1:
                        print(f"⚠️  {model} {err_type}, falling back to {model_chain[i+1]}...")
                    else:
                        tried = ', '.join(model_chain)
                        print(f"❌ All models exhausted. Tried: {tried}")
                        raise HTTPException(
                            status_code=503,
                            detail=(
                                "All AI models are currently unavailable or rate-limited. "
                                "Please wait 60 seconds and try again. "
                                f"Tried: {tried}"
                            )
                        )
                    break  # Move to next model immediately on 404




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

# --- Helper to encode PIL images ---
def encode_image(img: Image.Image) -> str:
    """Convert any PIL image mode to JPEG-compatible RGB before base64 encoding."""
    buffered = BytesIO()
    # JPEG only supports RGB and L (greyscale). Convert everything else.
    if img.mode == 'RGBA':
        # Composite onto white background to flatten alpha
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img = background
    elif img.mode == 'LA':
        background = Image.new('L', img.size, 255)
        background.paste(img, mask=img.split()[1])
        img = background.convert('RGB')
    elif img.mode == 'P':
        # Palette mode — convert to RGBA first to preserve transparency, then to RGB
        img = img.convert('RGBA')
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img = background
    elif img.mode not in ('RGB', 'L'):
        # CMYK, YCbCr, HSV, etc.
        img = img.convert('RGB')
    img.save(buffered, format="JPEG", quality=90)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')


# --- Core AI Functions ---

def get_invoice_data_from_text(text: str) -> InvoiceExtractionResponse:
    """
    Sends text to OpenRouter and returns validated Pydantic model.
    """
    
    # Check if client is initialized
    if client is None:
        raise HTTPException(
            status_code=500,
            detail="OpenRouter API client not initialized. Please check your OPENROUTER_API_KEY."
        )
    
    final_prompt = TEXT_PROMPT_TEMPLATE.format(invoice_text=text)
    
    try:
        response = _chat_with_retry(
            messages=[{"role": "user", "content": final_prompt}],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        
        json_output = response.choices[0].message.content.strip()
        
        print(f"--- 🔍 Raw OpenRouter Response (TEXT): {json_output} ---")
        
        if not json_output:
            raise ValueError("OpenRouter returned an empty response")
        
        if json_output.startswith("```json"):
            json_output = json_output[7:-3].strip()
        elif json_output.startswith("```"):
            json_output = json_output[3:-3].strip()
            
        if json_output.startswith("{{") and json_output.endswith("}}"):
            json_output = json_output[1:-1].strip()
            
        data = json.loads(json_output)
        validated_data = InvoiceExtractionResponse(**data)
        
        print("--- ✅ Successfully processed TEXT ---")
        return validated_data

    except HTTPException:
        raise  # Re-raise 503 rate limit errors directly
    except json.JSONDecodeError as e:
        print(f"--- ❌ JSON Decode Error (TEXT): {e} ---")
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response as JSON: {e}")
    except Exception as e:
        print(f"--- ❌ An error occurred during TEXT processing: {e} ---")
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")


def get_invoice_data_from_images(images: List[Image.Image]) -> InvoiceExtractionResponse:
    """
    Sends images to OpenRouter (multimodal) and returns validated data.
    """
    
    # Check if client is initialized
    if client is None:
        raise HTTPException(
            status_code=500,
            detail="OpenRouter API client not initialized. Please check your OPENROUTER_API_KEY."
        )
    
    content = [{"type": "text", "text": IMAGE_PROMPT_TEMPLATE}]
    
    for img in images:
        base64_img = encode_image(img)
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_img}"
            }
        })
        
    try:
        response = _chat_with_retry(
            messages=[{"role": "user", "content": content}],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        
        json_output = response.choices[0].message.content.strip()
        
        print(f"--- 🔍 Raw OpenRouter Response (IMAGE): {json_output} ---")
        
        if not json_output:
            raise ValueError("OpenRouter returned an empty response")
        
        if json_output.startswith("```json"):
            json_output = json_output[7:-3].strip()
        elif json_output.startswith("```"):
            json_output = json_output[3:-3].strip()
            
        if json_output.startswith("{{") and json_output.endswith("}}"):
            json_output = json_output[1:-1].strip()
            
        data = json.loads(json_output)
        validated_data = InvoiceExtractionResponse(**data)
        
        print("--- ✅ Successfully processed IMAGE(S) ---")
        return validated_data

    except HTTPException:
        raise  # Re-raise 503 rate limit errors directly
    except json.JSONDecodeError as e:
        print(f"--- ❌ JSON Decode Error (IMAGE): {e} ---")
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response as JSON: {e}")
    except Exception as e:
        print(f"--- ❌ An error occurred during IMAGE processing: {e} ---")
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")


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
