"""
Gmail Authentication Setup Script
==================================
This script helps you set up Gmail API authentication properly.
Run this FIRST before using the email poller.

It will:
1. Open a browser window for OAuth authorization
2. Generate a token.json file with refresh token
3. Test the connection to Gmail API
"""

import os
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# File paths
SCRIPT_DIR = os.path.dirname(__file__)
CREDENTIALS_FILE = os.path.join(SCRIPT_DIR, 'credentials.json')
TOKEN_FILE = os.path.join(SCRIPT_DIR, 'token.json')

def authenticate():
    """Run the OAuth flow to authenticate and save credentials."""
    print("=" * 70)
    print("  Gmail API Authentication Setup")
    print("=" * 70)
    
    # Check if credentials file exists
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"\n❌ ERROR: credentials.json not found!")
        print(f"   Expected location: {CREDENTIALS_FILE}")
        print("\n📋 To fix this:")
        print("   1. Go to Google Cloud Console")
        print("   2. Enable Gmail API for your project")
        print("   3. Create OAuth 2.0 credentials")
        print("   4. Download the credentials JSON file")
        print("   5. Save it as 'credentials.json' in the worker directory")
        sys.exit(1)
    
    print(f"\n✅ Found credentials file: {CREDENTIALS_FILE}")
    
    # Delete old token if it exists
    if os.path.exists(TOKEN_FILE):
        print(f"\n⚠️  Existing token.json found. Deleting it to create fresh credentials...")
        os.remove(TOKEN_FILE)
    
    print("\n🔐 Starting OAuth flow...")
    print("   A browser window will open shortly.")
    print("   Please sign in with your Gmail account and authorize the app.")
    print("   Make sure to grant ALL requested permissions.\n")
    
    try:
        # Create OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE, 
            SCOPES
        )
        
        # Run the local server on port 8080
        # access_type='offline' ensures we get a refresh token
        # prompt='consent' forces the consent screen to show, ensuring refresh token
        creds = flow.run_local_server(
            port=8080,
            access_type='offline',
            prompt='consent'
        )
        
        print("\n✅ Authorization successful!")
        
        # Save the credentials
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        
        print(f"✅ Token saved to: {TOKEN_FILE}")
        
        # Verify the token has a refresh token
        import json
        with open(TOKEN_FILE, 'r') as f:
            token_data = json.load(f)
        
        if 'refresh_token' in token_data:
            print("✅ Refresh token is present - credentials are valid!")
        else:
            print("⚠️  Warning: No refresh token found.")
            print("   This might happen if you've authorized this app before.")
            print("   The credentials should still work, but may need re-authorization later.")
        
        # Test the connection
        print("\n🧪 Testing Gmail API connection...")
        service = build('gmail', 'v1', credentials=creds)
        
        # Try to get user profile
        profile = service.users().getProfile(userId='me').execute()
        email = profile.get('emailAddress', 'Unknown')
        
        print(f"✅ Successfully connected to Gmail!")
        print(f"   Email: {email}")
        print(f"   Total messages: {profile.get('messagesTotal', 0)}")
        
        print("\n" + "=" * 70)
        print("  🎉 Authentication Complete!")
        print("=" * 70)
        print("\nYou can now:")
        print("  1. Run the email poller worker script")
        print("  2. Use the 'Check Email' button in your frontend")
        print("\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Authentication failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("   1. Make sure credentials.json is valid")
        print("   2. Ensure port 8080 is not in use by another application")
        print("   3. Check that http://localhost:8080/ is in your OAuth redirect URIs")
        print("   4. Try running this script again")
        print("\n")
        return False

if __name__ == "__main__":
    success = authenticate()
    sys.exit(0 if success else 1)
