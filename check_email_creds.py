"""
Quick script to check email credentials in database
"""
import sys
sys.path.insert(0, '/home/ashwarygupta/Coding/ML/FastAPI Implementation/Invox/backend2')

from app.db.session import SessionLocal
from app.models.email_credential import EmailCredential

db = SessionLocal()

try:
    # Get all email credentials
    credentials = db.query(EmailCredential).all()
    
    print(f"Found {len(credentials)} email credential(s)\n")
    
    for cred in credentials:
        print(f"=" * 80)
        print(f"ID: {cred.id}")
        print(f"User ID: {cred.user_id}")
        print(f"Email: {cred.email_address}")
        print(f"Provider: {cred.provider}")
        print(f"OAuth Token: {'SET ✅' if cred.oauth_token else 'NULL ❌'}")
        print(f"OAuth Expiry: {cred.oauth_token_expiry if cred.oauth_token_expiry else 'NULL'}")
        print(f"IMAP Server: {cred.imap_server if cred.imap_server else 'NULL'}")
        print(f"IMAP Password: {'SET ✅' if cred.imap_password else 'NULL ❌'}")
        print(f"Polling Enabled: {cred.polling_enabled}")
        print(f"Active: {cred.is_active}")
        print(f"Last Poll Status: {cred.last_poll_status if cred.last_poll_status else 'NULL'}")
        print(f"Last Error: {cred.last_error if cred.last_error else 'NULL'}")
        print(f"Created: {cred.created_at}")
        print(f"Updated: {cred.updated_at}")
        print()
        
finally:
    db.close()
