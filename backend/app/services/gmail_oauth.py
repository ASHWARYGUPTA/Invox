"""
Gmail OAuth Service for backend2
Handles Gmail API authentication and email retrieval using OAuth 2.0
"""
import os
import base64
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sqlalchemy.orm import Session

from app.services.encryption import encryption_service
from app.models.email_credential import EmailCredential


class GmailOAuthService:
    """
    Service for Gmail OAuth authentication and email operations
    """
    
    # Gmail API scopes
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    
    def __init__(self, db: Session, email_credential: EmailCredential):
        """
        Initialize Gmail OAuth service
        
        Args:
            db: Database session
            email_credential: EmailCredential model instance
        """
        self.db = db
        self.email_credential = email_credential
        self.service = None
    
    @staticmethod
    def get_authorization_url(client_config: dict, state: str, redirect_uri: str) -> str:
        """
        Generate OAuth authorization URL for Gmail
        
        Args:
            client_config: OAuth client configuration from Google Cloud Console
            state: CSRF protection state token
            redirect_uri: OAuth redirect URI (from settings)
            
        Returns:
            Authorization URL for user to visit
        """
        flow = Flow.from_client_config(
            client_config,
            scopes=GmailOAuthService.SCOPES,
            redirect_uri=redirect_uri
        )
        
        # Generate authorization URL
        # Note: include_granted_scopes='false' to prevent Google from adding extra scopes
        # But Google may still add OpenID Connect scopes (openid, profile, email) automatically
        authorization_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='false',  # Changed to 'false' to minimize scope changes
            prompt='consent',  # Force consent to get refresh token
            state=state
        )
        
        return authorization_url
    
    @staticmethod
    def exchange_code_for_tokens(client_config: dict, code: str, state: str, redirect_uri: str) -> dict:
        """
        Exchange authorization code for access and refresh tokens
        
        Args:
            client_config: OAuth client configuration
            code: Authorization code from OAuth callback
            state: State token for verification (currently not used by Flow)
            redirect_uri: OAuth redirect URI (from settings)
            
        Returns:
            Token dictionary with access_token, refresh_token, etc.
        """
        # Create flow WITHOUT state parameter to avoid scope validation issues
        # Google may add additional scopes (openid, userinfo.profile, userinfo.email)
        # and the Flow library's state validation includes scope checking which is too strict
        flow = Flow.from_client_config(
            client_config,
            scopes=GmailOAuthService.SCOPES,
            redirect_uri=redirect_uri
        )
        
        # Fetch tokens - this will accept whatever scopes Google returns
        # Pass state as None to skip internal state/scope validation
        flow.fetch_token(code=code)
        
        credentials = flow.credentials
        
        # Store all scopes returned by Google (may include openid scopes)
        return {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes,  # This will include all scopes Google granted
            'expiry': credentials.expiry.isoformat() if credentials.expiry else None
        }
    
    def _get_credentials(self) -> Optional[Credentials]:
        """
        Get valid OAuth credentials, refreshing if necessary
        
        Returns:
            Valid Credentials object or None if authentication fails
        """
        if not self.email_credential.oauth_token:
            print(f"❌ No OAuth token found for {self.email_credential.email_address}")
            return None
        
        try:
            # Decrypt and parse OAuth token
            decrypted_token = encryption_service.decrypt(self.email_credential.oauth_token)
            token_data = json.loads(decrypted_token)
            
            # Create credentials object
            creds = Credentials(
                token=token_data.get('token'),
                refresh_token=token_data.get('refresh_token'),
                token_uri=token_data.get('token_uri'),
                client_id=token_data.get('client_id'),
                client_secret=token_data.get('client_secret'),
                scopes=token_data.get('scopes')
            )
            
            # Check if token is expired or about to expire
            if creds.expiry:
                creds.expiry = datetime.fromisoformat(token_data.get('expiry'))
            
            # Refresh token if expired
            if not creds.valid:
                if creds.expired and creds.refresh_token:
                    print(f"🔄 Refreshing OAuth token for {self.email_credential.email_address}")
                    creds.refresh(Request())
                    
                    # Update stored credentials
                    updated_token_data = {
                        'token': creds.token,
                        'refresh_token': creds.refresh_token,
                        'token_uri': creds.token_uri,
                        'client_id': creds.client_id,
                        'client_secret': creds.client_secret,
                        'scopes': creds.scopes,
                        'expiry': creds.expiry.isoformat() if creds.expiry else None
                    }
                    
                    encrypted_token = encryption_service.encrypt(json.dumps(updated_token_data))
                    self.email_credential.oauth_token = encrypted_token
                    self.email_credential.oauth_token_expiry = creds.expiry
                    self.db.commit()
                    
                    print(f"✅ Token refreshed successfully")
                else:
                    print(f"❌ Token expired and no refresh token available")
                    return None
            
            return creds
            
        except Exception as e:
            print(f"❌ Error getting credentials: {e}")
            return None
    
    def connect(self) -> bool:
        """
        Connect to Gmail API using OAuth credentials
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            creds = self._get_credentials()
            if not creds:
                return False
            
            # Build Gmail service
            self.service = build('gmail', 'v1', credentials=creds)
            
            # Test connection by getting profile
            profile = self.service.users().getProfile(userId='me').execute()
            email = profile.get('emailAddress')
            
            print(f"✅ Connected to Gmail API: {email}")
            return True
            
        except Exception as e:
            print(f"❌ Gmail API connection failed: {e}")
            self.email_credential.last_error = str(e)
            self.email_credential.last_poll_status = "error"
            self.db.commit()
            return False
    
    def disconnect(self):
        """Close Gmail API connection"""
        self.service = None
    
    def get_unread_messages(self, max_results: int = 10) -> List[Dict]:
        """
        Get unread messages from Gmail
        
        Args:
            max_results: Maximum number of messages to retrieve
            
        Returns:
            List of message data dictionaries
        """
        if not self.service:
            raise ValueError("Not connected to Gmail API. Call connect() first.")
        
        try:
            # Get list of unread messages
            response = self.service.users().messages().list(
                userId='me',
                labelIds=['UNREAD'],
                maxResults=max_results
            ).execute()
            
            messages = response.get('messages', [])
            
            if not messages:
                return []
            
            # Get full message data for each message
            full_messages = []
            for msg in messages:
                msg_data = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                full_messages.append(msg_data)
            
            return full_messages
            
        except HttpError as error:
            print(f"❌ Error fetching messages: {error}")
            return []
    
    def get_message_attachments(self, message_id: str) -> List[Tuple[str, bytes]]:
        """
        Get all attachments from a Gmail message
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            List of (filename, file_bytes) tuples
        """
        if not self.service:
            raise ValueError("Not connected to Gmail API. Call connect() first.")
        
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            attachments = []
            
            # Process message parts
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part.get('filename'):
                        filename = part['filename']
                        
                        if 'attachmentId' in part['body']:
                            attachment_id = part['body']['attachmentId']
                            
                            # Download attachment
                            att = self.service.users().messages().attachments().get(
                                userId='me',
                                messageId=message_id,
                                id=attachment_id
                            ).execute()
                            
                            file_data = base64.urlsafe_b64decode(att['data'].encode('UTF-8'))
                            attachments.append((filename, file_data))
            
            return attachments
            
        except HttpError as error:
            print(f"❌ Error fetching attachments: {error}")
            return []
    
    def mark_as_read(self, message_id: str) -> bool:
        """
        Mark a Gmail message as read
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            raise ValueError("Not connected to Gmail API. Call connect() first.")
        
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            
            return True
            
        except HttpError as error:
            print(f"❌ Error marking message as read: {error}")
            return False
    
    def get_message_details(self, message_data: dict) -> Dict[str, str]:
        """
        Extract message details from Gmail message data
        
        Args:
            message_data: Full message data from Gmail API
            
        Returns:
            Dictionary with subject, from, date, etc.
        """
        headers = message_data['payload']['headers']
        
        details = {
            'id': message_data['id'],
            'subject': next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject'),
            'from': next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown'),
            'date': next((h['value'] for h in headers if h['name'] == 'Date'), None),
            'message_id': next((h['value'] for h in headers if h['name'] == 'Message-ID'), None)
        }
        
        return details
