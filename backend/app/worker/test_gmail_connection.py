"""
Test script to verify Gmail API setup is working correctly.
Run this to ensure the email poller can connect to Gmail.
"""

import os
import sys

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, project_root)

def test_gmail_connection():
    """Test the Gmail API connection."""
    print("=" * 70)
    print("  Testing Gmail API Connection")
    print("=" * 70)
    
    try:
        from app.worker.email_poller import get_gmail_service
        
        print("\n1️⃣  Loading Gmail service...")
        service = get_gmail_service()
        
        if not service:
            print("❌ Failed to get Gmail service")
            return False
        
        print("✅ Gmail service loaded successfully")
        
        print("\n2️⃣  Testing API call...")
        profile = service.users().getProfile(userId='me').execute()
        
        email = profile.get('emailAddress', 'Unknown')
        total_messages = profile.get('messagesTotal', 0)
        
        print(f"✅ Successfully connected to Gmail!")
        print(f"   Email: {email}")
        print(f"   Total messages: {total_messages}")
        
        print("\n3️⃣  Checking for unread messages...")
        response = service.users().messages().list(
            userId='me',
            labelIds=['UNREAD'],
            maxResults=5
        ).execute()
        
        unread_count = len(response.get('messages', []))
        print(f"✅ Found {unread_count} unread message(s)")
        
        print("\n" + "=" * 70)
        print("  ✅ All tests passed! Gmail API is working correctly.")
        print("=" * 70)
        print("\nYou can now:")
        print("  - Use the 'Check Email' button in the frontend")
        print("  - Run the email poller worker: python app\\worker\\email_poller.py")
        print()
        
        return True
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\n📋 Solution:")
        print("   Run the authentication script first:")
        print("   python app\\worker\\authenticate_gmail.py")
        return False
        
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("\n📋 Solution:")
        print("   Your token.json file is corrupted or invalid.")
        print("   Delete it and re-authenticate:")
        print("   1. Remove-Item app\\worker\\token.json")
        print("   2. python app\\worker\\authenticate_gmail.py")
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        print("\n📋 Check:")
        print("   1. credentials.json is in app/worker/")
        print("   2. token.json exists and is valid")
        print("   3. Gmail API is enabled in Google Cloud Console")
        return False

if __name__ == "__main__":
    success = test_gmail_connection()
    sys.exit(0 if success else 1)
