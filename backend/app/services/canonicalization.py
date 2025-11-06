# /backend/app/services/canonicalization.py
"""
Data Canonicalization Service
Ensures all invoice data follows consistent standards
"""

import re
from datetime import datetime, date
from typing import Optional, Tuple
from decimal import Decimal, InvalidOperation

# ISO 4217 Currency Codes Mapping
CURRENCY_MAPPINGS = {
    # USD variations
    "USD": "USD", "$": "USD", "US": "USD", "DOLLAR": "USD", "DOLLARS": "USD", "US DOLLAR": "USD",
    # INR variations
    "INR": "INR", "₹": "INR", "RS": "INR", "RUPEE": "INR", "RUPEES": "INR", "INDIAN RUPEE": "INR",
    # EUR variations
    "EUR": "EUR", "€": "EUR", "EURO": "EUR", "EUROS": "EUR",
    # GBP variations
    "GBP": "GBP", "£": "GBP", "POUND": "GBP", "POUNDS": "GBP", "STERLING": "GBP",
    # Other common currencies
    "CAD": "CAD", "AUD": "AUD", "JPY": "JPY", "¥": "JPY", "YEN": "JPY",
    "CNY": "CNY", "YUAN": "CNY",
    "CHF": "CHF", "FRANC": "CHF",
    "SGD": "SGD",
    "AED": "AED", "DIRHAM": "AED",
}


def normalize_currency_code(currency: Optional[str]) -> str:
    """
    Normalize currency to ISO 4217 standard (3-letter code).
    
    Args:
        currency: Raw currency string from AI extraction
        
    Returns:
        ISO 4217 currency code (e.g., "USD", "INR", "EUR")
        Defaults to "USD" if not recognized
    """
    if not currency:
        return "USD"
    
    # Clean and uppercase
    currency_clean = currency.strip().upper()
    
    # Remove common prefixes/suffixes
    currency_clean = currency_clean.replace("CURRENCY:", "").strip()
    
    # Direct lookup
    if currency_clean in CURRENCY_MAPPINGS:
        return CURRENCY_MAPPINGS[currency_clean]
    
    # Try to extract 3-letter code if embedded in text
    iso_match = re.search(r'\b([A-Z]{3})\b', currency_clean)
    if iso_match:
        code = iso_match.group(1)
        if code in CURRENCY_MAPPINGS:
            return CURRENCY_MAPPINGS[code]
    
    # Check for currency symbols in text
    for key, value in CURRENCY_MAPPINGS.items():
        if key in currency_clean:
            return value
    
    # Default to USD if unknown
    print(f"⚠️  Unknown currency '{currency}', defaulting to USD")
    return "USD"


def normalize_date(date_str: Optional[str]) -> Optional[date]:
    """
    Normalize date to ISO 8601 format (YYYY-MM-DD).
    
    Handles various date formats:
    - ISO: 2024-12-31, 2024/12/31
    - US: 12/31/2024, 12-31-2024
    - EU: 31/12/2024, 31-12-2024
    - Verbose: December 31, 2024
    
    Args:
        date_str: Raw date string from AI extraction
        
    Returns:
        Python date object or None if parsing fails
    """
    if not date_str:
        return None
    
    # Clean the input
    date_clean = date_str.strip()
    
    # If already a date object, return it
    if isinstance(date_clean, date):
        return date_clean
    
    # Try various date formats
    date_formats = [
        "%Y-%m-%d",           # 2024-12-31 (ISO)
        "%Y/%m/%d",           # 2024/12/31
        "%d-%m-%Y",           # 31-12-2024 (EU)
        "%d/%m/%Y",           # 31/12/2024 (EU)
        "%m-%d-%Y",           # 12-31-2024 (US)
        "%m/%d/%Y",           # 12/31/2024 (US)
        "%B %d, %Y",          # December 31, 2024
        "%b %d, %Y",          # Dec 31, 2024
        "%d %B %Y",           # 31 December 2024
        "%d %b %Y",           # 31 Dec 2024
        "%Y%m%d",             # 20241231
    ]
    
    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(date_clean, fmt).date()
            return parsed_date
        except ValueError:
            continue
    
    # If all formats fail, log and return None
    print(f"⚠️  Could not parse date '{date_str}', setting to None")
    return None


def normalize_amount(amount: Optional[float]) -> Optional[float]:
    """
    Normalize monetary amount to consistent decimal format.
    
    - Ensures proper decimal precision (2 decimal places)
    - Handles negative amounts
    - Validates numeric range
    
    Args:
        amount: Raw amount from AI extraction
        
    Returns:
        Normalized float with 2 decimal places or None if invalid
    """
    if amount is None:
        return None
    
    try:
        # Convert to Decimal for precise arithmetic
        decimal_amount = Decimal(str(amount))
        
        # Round to 2 decimal places
        rounded = round(float(decimal_amount), 2)
        
        # Validate range (assuming invoices shouldn't be negative or extremely large)
        if rounded < 0:
            print(f"⚠️  Negative amount detected: {rounded}, keeping as-is")
        
        if rounded > 999999999.99:
            print(f"⚠️  Unusually large amount: {rounded}, please verify")
        
        return rounded
    
    except (InvalidOperation, ValueError, TypeError) as e:
        print(f"⚠️  Could not normalize amount '{amount}': {e}")
        return None


def normalize_text_field(text: Optional[str], title_case: bool = True) -> Optional[str]:
    """
    Normalize text fields (vendor names, invoice IDs).
    
    - Strips whitespace
    - Removes extra spaces
    - Optionally converts to title case
    - Removes special characters if needed
    
    Args:
        text: Raw text string
        title_case: Whether to convert to title case (for vendor names)
        
    Returns:
        Cleaned and normalized text or None
    """
    if not text:
        return None
    
    # Strip and normalize whitespace
    normalized = " ".join(text.strip().split())
    
    # Apply title case for vendor names (not for invoice IDs)
    if title_case and len(normalized) > 0:
        # Only title case if it looks like a name (contains letters)
        if any(c.isalpha() for c in normalized):
            normalized = normalized.title()
    
    return normalized if normalized else None


def canonicalize_invoice_data(
    invoice_id: Optional[str],
    vendor_name: Optional[str],
    amount_due: Optional[float],
    due_date: Optional[str],
    invoice_date: Optional[str],
    currency_code: Optional[str],
    confidence_score: Optional[float]
) -> dict:
    """
    Apply all canonicalization rules to invoice data.
    
    This is the main function that should be called to normalize
    all invoice fields before saving to database.
    
    Args:
        All invoice fields as extracted by AI
        
    Returns:
        Dictionary with canonicalized fields
    """
    return {
        "invoice_id": normalize_text_field(invoice_id, title_case=False),
        "vendor_name": normalize_text_field(vendor_name, title_case=True),
        "amount_due": normalize_amount(amount_due),
        "due_date": normalize_date(due_date),
        "invoice_date": normalize_date(invoice_date),
        "currency_code": normalize_currency_code(currency_code),
        "confidence_score": round(confidence_score, 4) if confidence_score is not None else 0.0,
    }


# Validation helper
def validate_canonicalized_data(data: dict) -> Tuple[bool, Optional[str]]:
    """
    Validate that canonicalized data meets minimum requirements.
    
    Returns:
        (is_valid, error_message)
    """
    # Must have either invoice_id OR (vendor_name AND amount_due)
    has_invoice_id = data.get("invoice_id") is not None
    has_vendor_and_amount = (
        data.get("vendor_name") is not None 
        and data.get("amount_due") is not None
    )
    
    if not (has_invoice_id or has_vendor_and_amount):
        return False, "Invoice must have invoice_id OR both vendor_name and amount_due"
    
    # Validate currency code format (must be 3 uppercase letters)
    currency = data.get("currency_code", "USD")
    if not (isinstance(currency, str) and len(currency) == 3 and currency.isupper()):
        return False, f"Invalid currency code: {currency}"
    
    return True, None
