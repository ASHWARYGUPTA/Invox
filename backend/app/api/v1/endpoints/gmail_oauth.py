"""
Gmail OAuth API Endpoints
Handles OAuth flow for Gmail authentication
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
import secrets
import json

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.services.gmail_oauth import GmailOAuthService
from app.services.encryption import encryption_service
from app.crud import email_credential
from app.core.config import settings

router = APIRouter()


class GmailAuthUrlResponse(BaseModel):
    """Response for Gmail authorization URL"""
    auth_url: str
    state: str


class GmailCallbackRequest(BaseModel):
    """Request body for Gmail OAuth callback"""
    code: str
    state: str


class GmailCallbackResponse(BaseModel):
    """Response for successful OAuth callback"""
    success: bool
    message: str
    email_address: str


@router.get("/gmail/auth-url", response_model=GmailAuthUrlResponse)
def get_gmail_auth_url(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate Gmail OAuth authorization URL
    
    Returns URL for frontend to open in popup/redirect
    """
    
    # Generate CSRF state token
    state = secrets.token_urlsafe(32)
    
    # TODO: Store state in Redis/cache with user_id for verification
    # For now, we'll verify it in callback
    
    # Get OAuth client config from environment
    client_config = {
        "web": {
            "client_id": settings.GMAIL_CLIENT_ID,
            "client_secret": settings.GMAIL_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.GMAIL_REDIRECT_URI]
        }
    }
    
    # Generate authorization URL
    auth_url = GmailOAuthService.get_authorization_url(
        client_config, 
        state, 
        settings.GMAIL_REDIRECT_URI
    )
    
    return GmailAuthUrlResponse(
        auth_url=auth_url,
        state=state
    )


@router.post("/gmail/callback", response_model=GmailCallbackResponse)
def handle_gmail_callback(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    callback_data: GmailCallbackRequest
):
    """
    Handle OAuth callback from Gmail
    
    Exchanges authorization code for tokens and stores in database
    """
    
    print(f"🔔 Gmail OAuth callback received for user {current_user.id}")
    print(f"   Code: {callback_data.code[:20]}...")
    print(f"   State: {callback_data.state}")
    
    # TODO: Verify state token matches what we generated
    # For production, check against Redis/cache
    
    try:
        # Get OAuth client config
        client_config = {
            "web": {
                "client_id": settings.GMAIL_CLIENT_ID,
                "client_secret": settings.GMAIL_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.GMAIL_REDIRECT_URI]
            }
        }
        
        # Exchange code for tokens
        tokens = GmailOAuthService.exchange_code_for_tokens(
            client_config,
            callback_data.code,
            callback_data.state,
            settings.GMAIL_REDIRECT_URI
        )
        
        # Get user's email from Gmail API
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        
        creds = Credentials(
            token=tokens['token'],
            refresh_token=tokens['refresh_token'],
            token_uri=tokens['token_uri'],
            client_id=tokens['client_id'],
            client_secret=tokens['client_secret'],
            scopes=tokens['scopes']
        )
        
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        email_address = profile.get('emailAddress')
        
        # Encrypt tokens
        tokens_json = json.dumps(tokens)
        encrypted_tokens = encryption_service.encrypt(tokens_json)
        
        print(f"✅ Got tokens for {email_address}")
        print(f"   Token length: {len(encrypted_tokens)} chars (encrypted)")
        
        # Check if email config already exists
        existing = email_credential.get_email_credential(db, current_user.id)
        
        if existing:
            # Update existing configuration
            from app.schemas.email_credential import EmailCredentialUpdate
            from datetime import datetime
            
            print(f"📝 Updating existing email credential for user {current_user.id}")
            
            update_data = EmailCredentialUpdate(
                email_address=email_address,
                provider="gmail",
                oauth_token=encrypted_tokens,
                oauth_token_expiry=datetime.fromisoformat(tokens['expiry']) if tokens.get('expiry') else None,
                # Clear IMAP fields when switching to OAuth
                imap_password=None,
                imap_server=None,
                imap_port=None,
                imap_username=None
            )
            
            print(f"   OAuth token in update_data: {update_data.oauth_token[:50]}... (length: {len(update_data.oauth_token) if update_data.oauth_token else 0})")
            
            email_credential.update_email_credential(
                db=db,
                user_id=current_user.id,
                credential_update=update_data
            )
            
            print(f"✅ Updated email credential with OAuth token")
        else:
            # Create new configuration
            from app.schemas.email_credential import EmailCredentialCreate
            from datetime import datetime
            
            create_data = EmailCredentialCreate(
                email_address=email_address,
                provider="gmail",
                oauth_token=encrypted_tokens,
                oauth_token_expiry=datetime.fromisoformat(tokens['expiry']) if tokens.get('expiry') else None,
                polling_enabled=True,
                polling_interval_minutes=5,
                folder_to_watch="INBOX",
                mark_as_read=True
            )
            
            email_credential.create_email_credential(
                db=db,
                user_id=current_user.id,
                credential_data=create_data
            )
        
        return GmailCallbackResponse(
            success=True,
            message="Gmail account connected successfully!",
            email_address=email_address
        )
        
    except Exception as e:
        print(f"❌ Gmail OAuth callback error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth callback failed: {str(e)}"
        )


@router.post("/gmail/disconnect", response_model=dict)
def disconnect_gmail(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Disconnect Gmail OAuth account
    
    Clears OAuth tokens but keeps email config for potential re-authorization
    """
    
    existing = email_credential.get_email_credential(db, current_user.id)
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email configuration not found"
        )
    
    if existing.provider != "gmail" or not existing.oauth_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not a Gmail OAuth account"
        )
    
    # Clear OAuth tokens
    from app.schemas.email_credential import EmailCredentialUpdate
    
    update_data = EmailCredentialUpdate(
        oauth_token=None,
        oauth_token_expiry=None,
        polling_enabled=False,
        is_active=False
    )
    
    email_credential.update_email_credential(
        db=db,
        user_id=current_user.id,
        credential_update=update_data
    )
    
    return {
        "success": True,
        "message": "Gmail account disconnected"
    }
