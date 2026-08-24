import os
import asyncio
from dotenv import load_dotenv

# Load the environment variables from .env
load_dotenv()

# Set up the Python path so it can find the app module
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.invoice_processing import get_invoice_data_from_text

# Create a sample text-based invoice
SAMPLE_INVOICE_TEXT = """
ACME Corp
123 Business Rd, Metropolis, NY 10001
Phone: (555) 123-4567

INVOICE
Invoice Number: INV-2023-0842
Date: 2023-11-15
Due Date: 2023-12-15

Bill To:
Wayne Enterprises
1007 Mountain Drive, Gotham

Description                         Qty     Unit Price      Total
------------------------------------------------------------------
High-Performance Batarangs          50      $12.50          $625.00
Grappling Hook Replacement Cables   10      $45.00          $450.00
Tactical Smoke Pellets              100     $3.00           $300.00
------------------------------------------------------------------
Subtotal:                                                   $1,375.00
Tax (8.875%):                                               $122.03
Total Due:                                                  $1,497.03

Please make checks payable to ACME Corp. Thank you for your business!
"""

def run_test():
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or api_key == "your-openrouter-key-here":
        print("❌ Please set your actual OPENROUTER_API_KEY in the backend/.env file before running this test.")
        return

    print("🚀 Running OpenRouter Invoice Extraction Test...")
    print(f"📄 Sample Invoice Text Length: {len(SAMPLE_INVOICE_TEXT)} characters")
    
    try:
        # Call the processing function
        result = get_invoice_data_from_text(SAMPLE_INVOICE_TEXT)
        
        print("\n✅ Extraction Successful! Result:\n")
        print(f"Vendor Name:      {result.vendor_name}")
        print(f"Invoice ID:       {result.invoice_id}")
        print(f"Invoice Date:     {result.invoice_date}")
        print(f"Due Date:         {result.due_date}")
        print(f"Amount Due:       {result.amount_due}")
        print(f"Currency:         {result.currency_code}")
        print(f"Confidence Score: {result.confidence_score}")
        
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")

if __name__ == "__main__":
    run_test()
