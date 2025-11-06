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
from app.crud import invoice as crud_invoice
from app.schemas.invoice import InvoiceCreate

# --- 1. Google API Configuration ---
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), 'credentials.json')
TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'token.json')

# --- 2. Set the Default User ID ---
# All invoices from this poller will be assigned to this user.
# In your database, this is almost certainly user ID 1.
DEFAULT_OWNER_ID = 1

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

def process_attachment(db: SessionLocal, service, user_id, msg_id, att_id, filename):
    """Downloads attachment and processes it *directly*."""
    print(f"  > Processing attachment: {filename}")
    
    att = service.users().messages().attachments().get(
        userId=user_id, messageId=msg_id, id=att_id
    ).execute()
    
    file_bytes = base64.urlsafe_b64decode(att['data'].encode('UTF-8'))
    
    # --- This logic is now direct ---
    try:
        if filename.lower().endswith('.pdf'):
            extracted_text = extract_text_from_pdf(file_bytes)
            if extracted_text and len(extracted_text) > 100:
                invoice_data = get_invoice_data_from_text(extracted_text)
            else:
                images = convert_pdf_to_images(file_bytes)
                invoice_data = get_invoice_data_from_images(images)
        
        elif filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image = Image.open(io.BytesIO(file_bytes))
            invoice_data = get_invoice_data_from_images([image])
        
        else:
            print(f"  > Skipping unsupported file type: {filename}")
            return False

        # 2. Create the InvoiceCreate schema
        invoice_to_create = InvoiceCreate(
            file_name=filename,
            **invoice_data.model_dump()
        )
        
        # 3. Save to database, linked to the default user
        crud_invoice.create_invoice(db=db, invoice=invoice_to_create, owner_id=DEFAULT_OWNER_ID)
        print(f"  > ✅ Successfully processed and saved to DB for user {DEFAULT_OWNER_ID}.")
        return True

    except Exception as e:
        print(f"  > ❌ An error occurred during direct processing: {e}")
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

def check_for_invoices(service, db: SessionLocal, user_id='me'):
    """Finds unread emails, processes attachments, and marks as read."""
    print(f"\n--- 📧 Checking for new invoices... ---")
    try:
        response = service.users().messages().list(
            userId=user_id,
            labelIds=['UNREAD']
        ).execute()
        
        messages = response.get('messages', [])
        
        if not messages:
            print("--- No new emails found. ---")
            return

        print(f"--- Found {len(messages)} new email(s)! ---")
        
        for msg in messages:
            msg_id = msg['id']
            message = service.users().messages().get(userId=user_id, id=msg_id).execute()
            
            headers = message['payload']['headers']
            subject = next(h['value'] for h in headers if h['name'] == 'Subject')
            print(f"\nProcessing email (Subject: {subject})")
            
            parts = message['payload'].get('parts', [])
            processed_all = True
            
            for part in parts:
                if part['filename']:
                    if not process_attachment(db, service, user_id, msg_id, part['body']['attachmentId'], part['filename']):
                        processed_all = False
            
            if processed_all:
                mark_email_as_read(service, user_id, msg_id)
            else:
                print(f"  > ⚠️ Some attachments failed. Email {msg_id} will NOT be marked as read.")

    except HttpError as error:
        print(f"An error occurred searching emails: {error}")

# --- 5. Main Loop ---
if __name__ == "__main__":
    print("--- 🤖 Invoice Email Robot (Integrated): ON ---")
    service = get_gmail_service()
    
    if service:
        print("--- Press CTRL+C to stop. ---")
        while True:
            try:
                # Create a new DB session for this loop
                db = SessionLocal()
                check_for_invoices(service, db)
                db.close()
                
                print(f"--- Sleeping for 30 seconds... ---")
                time.sleep(30)
            except KeyboardInterrupt:
                print("\n--- 🤖 Invoice Email Robot: OFF ---")
                break
            except Exception as e:
                print(f"An error in main loop: {e}")
                if 'db' in locals():
                    db.close() # Ensure db is closed on error
                time.sleep(30)