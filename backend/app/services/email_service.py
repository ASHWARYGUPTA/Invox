import os
import base64
import requests
import time
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load .env variables
load_dotenv()

# --- 1. FastAPI Server Configuration ---
API_URL_PDF = "http://127.0.0.1:8000/process_pdf/"
API_URL_IMAGE = "http://127.0.0.1:8000/process_image/"

# --- 2. Google API Configuration ---
# This scope allows reading emails AND marking them as read
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
CREDENTIALS_FILE = 'credentials.json' # The file you just downloaded
TOKEN_FILE = 'token.json' # This file will be created automatically

def get_gmail_service():
    """Authenticates with the Gmail API and returns a service object."""
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # THIS IS THE PART THAT RUNS ONCE
            print("--- ❗️ First-time setup required ---")
            print("--- A browser window will open for you to authorize this script. ---")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('gmail', 'v1', credentials=creds)
        print("--- ✅ Gmail API Service Connected ---")
        return service
    except HttpError as error:
        print(f"An error occurred building the service: {error}")
        return None

def process_attachment(service, user_id, msg_id, att_id, filename):
    """Downloads an attachment and sends it to the FastAPI server."""
    print(f"  > Processing attachment: {filename}")
    
    # Get attachment data
    att = service.users().messages().attachments().get(
        userId=user_id, messageId=msg_id, id=att_id
    ).execute()
    
    file_bytes = base64.urlsafe_b64decode(att['data'].encode('UTF-8'))
    
    # Determine content type from filename
    content_type = ""
    if filename.lower().endswith('.pdf'):
        content_type = "application/pdf"
    elif filename.lower().endswith('.png'):
        content_type = "image/png"
    elif filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
        content_type = "image/jpeg"
    else:
        print(f"  > Skipping unsupported file type: {filename}")
        return False

    files = {'file': (filename, file_bytes, content_type)}
    
    try:
        if content_type == "application/pdf":
            response = requests.post(API_URL_PDF, files=files)
        else:
            response = requests.post(API_URL_IMAGE, files=files)

        if response.status_code == 200:
            print(f"  > ✅ Successfully processed by API. Data: {response.json()}")
            return True
        else:
            print(f"  > ❌ API Error (Status {response.status_code}): {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("--- ❌ CRITICAL: Cannot connect to FastAPI server ---")
        return False
    except Exception as e:
        print(f"  > ❌ An unknown error occurred: {e}")
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

def check_for_invoices(service, user_id='me'):
    """Finds unread emails, processes attachments, and marks as read."""
    print(f"\n--- 📧 Checking for new invoices... ---")
    try:
        # Search for unread emails
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
            # Get the full email message
            message = service.users().messages().get(userId=user_id, id=msg_id).execute()
            
            headers = message['payload']['headers']
            subject = next(h['value'] for h in headers if h['name'] == 'Subject')
            print(f"\nProcessing email (Subject: {subject})")
            
            parts = message['payload'].get('parts', [])
            processed_all = True
            
            for part in parts:
                if part['filename']: # This part is an attachment
                    if not process_attachment(service, user_id, msg_id, part['body']['attachmentId'], part['filename']):
                        processed_all = False # Don't mark as read if one fails
            
            if processed_all:
                mark_email_as_read(service, user_id, msg_id)
            else:
                print(f"  > ⚠️ Some attachments failed. Email {msg_id} will NOT be marked as read.")

    except HttpError as error:
        print(f"An error occurred searching emails: {error}")

# --- 5. Main Loop ---
if __name__ == "__main__":
    print("--- 🤖 Invoice Email Robot (Gmail API Edition): ON ---")
    service = get_gmail_service() # Authenticate and get the service
    
    if service:
        print("--- Press CTRL+C to stop. ---")
        while True:
            try:
                check_for_invoices(service)
                print(f"--- Sleeping for 30 seconds... ---")
                time.sleep(30)
            except KeyboardInterrupt:
                print("\n--- 🤖 Invoice Email Robot: OFF ---")
                break