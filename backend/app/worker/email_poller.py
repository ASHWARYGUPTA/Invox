import os
import base64
import time
import sys

# --- This is new: Add the parent directory to the path ---
# This lets us import from 'app.core', 'app.db', etc.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(project_root)
# --- End of new part ---

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from PIL import Image
import io

# --- Import our app's logic ---
from app.db.session import SessionLocal
from app.services.processing_service import (
    get_invoice_data_from_text, 
    get_invoice_data_from_images, 
    extract_text_from_pdf, 
    convert_pdf_to_images
)
from app.services.canonicalization import canonicalize_invoice_data, validate_canonicalized_data
from app.crud import invoice as crud_invoice
from app.schemas.invoice import InvoiceCreate
# Import models to ensure they're registered with SQLAlchemy
from app.models import user, invoice  # This ensures all relationships are loaded

# --- 1. Google API Configuration ---
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), 'credentials.json')
TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'token.json')

# --- 2. Set the Default User ID ---
# All invoices from this poller will be assigned to this user.
# In your database, this is almost certainly user ID 1.
DEFAULT_OWNER_ID = 1

# --- 3. Email Poller Configuration ---
MAX_EMAILS_TO_CHECK = 5  # Only check the 5 most recent unread emails
POLLING_INTERVAL = 30  # Check every 30 seconds

def get_gmail_service():
    """Authenticates with the Gmail API and returns a service object."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"❌ Token refresh failed: {e}")
                print("--- Deleting old token and re-authenticating... ---")
                os.remove(TOKEN_FILE)
                return get_gmail_service()  # Retry authentication
        else:
            print("--- ❗️ First-time setup required for email poller ---")
            print("--- A browser window will open to authorize this script. ---")
            print("--- IMPORTANT: Use port 8080 for authorization ---")
            
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            # Use a fixed port (8080) that matches your credentials.json redirect URIs
            creds = flow.run_local_server(port=8080)
        
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('gmail', 'v1', credentials=creds)
        print("--- ✅ Gmail API Service Connected (Worker) ---")
        return service
    except HttpError as error:
        print(f"An error occurred building the service: {error}")
        return None

def process_attachment(db, service, user_id, msg_id, att_id, filename):
    """
    Downloads attachment and processes it directly.
    
    Returns:
        True: Successfully processed and saved
        'duplicate': Duplicate invoice detected
        'not_invoice': File is not an invoice (no meaningful data)
        False: Error occurred during processing
    """
    print(f"  > Processing attachment: {filename}")
    
    try:
        att = service.users().messages().attachments().get(
            userId=user_id, messageId=msg_id, id=att_id
        ).execute()
        
        file_bytes = base64.urlsafe_b64decode(att['data'].encode('UTF-8'))
        
        # --- This logic is now direct ---
        if filename.lower().endswith('.pdf'):
            print(f"  > Detected PDF file: {filename}")
            extracted_text = extract_text_from_pdf(file_bytes)
            if extracted_text and len(extracted_text) > 100:
                print(f"  > PDF is text-based, extracted {len(extracted_text)} characters")
                invoice_data = get_invoice_data_from_text(extracted_text)
            else:
                print(f"  > PDF is scanned or has little text, converting to images")
                images = convert_pdf_to_images(file_bytes)
                invoice_data = get_invoice_data_from_images(images)
        
        elif filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            print(f"  > Detected image file: {filename}")
            image = Image.open(io.BytesIO(file_bytes))
            invoice_data = get_invoice_data_from_images([image])
        
        else:
            print(f"  > Skipping unsupported file type: {filename}")
            return False

        # Validate that we extracted meaningful invoice data
        # At minimum, we need either invoice_id OR (vendor_name AND amount_due)
        has_meaningful_data = (
            invoice_data.invoice_id is not None or 
            (invoice_data.vendor_name is not None and invoice_data.amount_due is not None)
        )
        
        if not has_meaningful_data:
            print(f"  > ⚠️  No meaningful invoice data found in {filename}")
            print(f"  >    Skipping - attachment doesn't appear to be an invoice")
            return 'not_invoice'

        # 2. Apply canonicalization to normalize data
        print(f"  > Applying data canonicalization...")
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
            print(f"  > ❌ Validation failed: {error_msg}")
            return False

        # 3. Create the InvoiceCreate schema with canonicalized data
        invoice_to_create = InvoiceCreate(
            file_name=filename,
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
        
        # 4. Save to database, linked to the default user
        created_invoice, is_duplicate = crud_invoice.create_invoice(db=db, invoice=invoice_to_create, owner_id=DEFAULT_OWNER_ID)
        
        if is_duplicate:
            print(f"  > ⚠️  Duplicate invoice detected!")
            print(f"  >    Invoice #{invoice_to_create.invoice_id} from {invoice_to_create.vendor_name}")
            print(f"  >    Already exists in DB with ID: {created_invoice.id}")
            print(f"  >    Skipping duplicate entry.")
            return 'duplicate'  # Return status code for duplicate
        else:
            print(f"  > ✅ Successfully processed and saved to DB with ID: {created_invoice.id}")
            print(f"  >    Invoice: {invoice_to_create.invoice_id or 'N/A'}")
            print(f"  >    Vendor: {invoice_to_create.vendor_name or 'N/A'}")
            print(f"  >    Amount: {invoice_to_create.currency_code} {invoice_to_create.amount_due or 0.0}")
            print(f"  >    Invoice Date: {invoice_to_create.invoice_date or 'N/A'}")
            print(f"  >    Due Date: {invoice_to_create.due_date or 'N/A'}")
            print(f"  >    Confidence: {invoice_to_create.confidence_score:.2%}")
            print(f"  >    Status: {invoice_to_create.status}")
            return True

    except Exception as e:
        print(f"  > ❌ Error processing attachment {filename}: {e}")
        import traceback
        traceback.print_exc()
        return False

def mark_email_as_read(service, user_id, msg_id):
    """Marks an email as read by removing the UNREAD label."""
    try:
        service.users().messages().modify(
            userId=user_id,
            id=msg_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
        print(f"  > Finished processing. Marking email {msg_id} as read.")
    except HttpError as error:
        print(f"  > ❌ Could not mark as read: {error}")

def check_for_invoices(service, db, user_id='me', max_emails=5):
    """Finds unread emails, processes attachments, and marks as read."""
    print(f"\n--- 📧 Checking for new invoices (max {max_emails} emails)... ---")
    try:
        response = service.users().messages().list(
            userId=user_id,
            labelIds=['UNREAD'],
            maxResults=max_emails  # Limit to only fetch recent emails
        ).execute()
        
        messages = response.get('messages', [])
        
        if not messages:
            print("--- No new emails found. ---")
            return 0

        print(f"--- Found {len(messages)} unread email(s)! Processing up to {max_emails}... ---")
        
        invoices_processed = 0
        duplicates_found = 0
        
        for msg in messages:
            msg_id = msg['id']
            message = service.users().messages().get(userId=user_id, id=msg_id).execute()
            
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            
            print(f"\n📬 Email: {subject}")
            print(f"   From: {sender}")
            
            parts = message['payload'].get('parts', [])
            
            # Check if email has attachments
            if not parts or not any(p.get('filename') for p in parts):
                print(f"   ⏭️  No attachments found, skipping...")
                continue
            
            has_invoice = False
            processed_all = True
            
            for part in parts:
                if part['filename']:
                    filename = part['filename']
                    # Only process invoice-like attachments
                    if filename.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg')):
                        result = process_attachment(db, service, user_id, msg_id, part['body']['attachmentId'], filename)
                        if result == True:
                            # Successfully processed and saved
                            has_invoice = True
                            invoices_processed += 1
                        elif result == 'duplicate':
                            # Duplicate detected - count it but don't save
                            has_invoice = True
                            duplicates_found += 1
                        elif result == 'not_invoice':
                            # Not an invoice (no meaningful data) - skip silently
                            print(f"   ⏭️  Skipped non-invoice file: {filename}")
                        else:
                            # Error occurred during processing
                            processed_all = False
                    else:
                        print(f"   ⏭️  Skipping unsupported file type: {filename}")
            
            if has_invoice:
                if processed_all:
                    mark_email_as_read(service, user_id, msg_id)
                else:
                    print(f"  > ⚠️ Some attachments failed. Email {msg_id} will NOT be marked as read.")
            else:
                print(f"   ℹ️  No invoice attachments found in this email.")
        
        if invoices_processed > 0:
            print(f"\n✅ Successfully processed {invoices_processed} new invoice(s) from {len(messages)} email(s)")
            if duplicates_found > 0:
                print(f"⚠️  Skipped {duplicates_found} duplicate invoice(s)")
        else:
            if duplicates_found > 0:
                print(f"\n⚠️  Found {duplicates_found} duplicate invoice(s), no new invoices added")
            else:
                print(f"\nℹ️  No invoices found in {len(messages)} email(s)")
        
        return invoices_processed

    except HttpError as error:
        print(f"An error occurred searching emails: {error}")
        return 0

# --- 5. Main Loop ---
if __name__ == "__main__":
    print("=" * 70)
    print("  🤖 Invoice Email Robot - Starting")
    print("=" * 70)
    print(f"  Settings:")
    print(f"    - Max emails per check: {MAX_EMAILS_TO_CHECK}")
    print(f"    - Polling interval: {POLLING_INTERVAL} seconds")
    print(f"    - Default user ID: {DEFAULT_OWNER_ID}")
    print("=" * 70)
    
    service = get_gmail_service()
    
    if service:
        print("\n✅ Gmail service connected successfully!")
        print("📧 Monitoring for new invoices...")
        print("⚠️  Press CTRL+C to stop.\n")
        
        while True:
            try:
                # Create a new DB session for this loop
                db = SessionLocal()
                invoices_count = check_for_invoices(service, db, max_emails=MAX_EMAILS_TO_CHECK)
                db.close()
                
                if invoices_count > 0:
                    print(f"\n🎉 {invoices_count} new invoice(s) added to database!")
                    print(f"💡 Refresh your frontend to see the new invoices.")
                
                print(f"\n😴 Sleeping for {POLLING_INTERVAL} seconds...")
                print("-" * 70)
                time.sleep(POLLING_INTERVAL)
                
            except KeyboardInterrupt:
                print("\n\n" + "=" * 70)
                print("  🛑 Invoice Email Robot - Stopped by user")
                print("=" * 70)
                break
            except Exception as e:
                print(f"\n❌ Error in main loop: {e}")
                import traceback
                traceback.print_exc()
                if 'db' in locals():
                    db.close() # Ensure db is closed on error
                print(f"\n⏳ Retrying in {POLLING_INTERVAL} seconds...")
                time.sleep(POLLING_INTERVAL)
    else:
        print("\n❌ Failed to connect to Gmail service. Please check your credentials.")
        print("   Run this script again to retry authorization.")