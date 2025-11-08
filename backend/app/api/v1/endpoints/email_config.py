"""
API endpoints for email configuration and polling
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.schemas.email_credential import (
    EmailCredentialCreate,
    EmailCredentialUpdate,
    EmailCredential,
    EmailPollingStats,
    EmailProcessingLogSchema
)
from app.crud import email_credential
from app.services.email_polling import EmailPollingService

router = APIRouter()


@router.post("", response_model=EmailCredential, status_code=status.HTTP_201_CREATED)
def create_email_config(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    credential_in: EmailCredentialCreate
):
    """
    Create email configuration for the current user
    """
    
    # Check if credentials already exist
    existing = email_credential.get_email_credential(db, current_user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email configuration already exists. Use PUT to update."
        )
    
    # Create credentials
    db_credential = email_credential.create_email_credential(
        db=db,
        user_id=current_user.id,
        credential_data=credential_in
    )
    
    return db_credential


@router.get("", response_model=EmailCredential)
def get_email_config(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get email configuration for the current user
    """
    
    db_credential = email_credential.get_email_credential(db, current_user.id)
    
    if not db_credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email configuration not found"
        )
    
    return db_credential


@router.put("", response_model=EmailCredential)
def update_email_config(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    credential_update: EmailCredentialUpdate
):
    """
    Update email configuration for the current user
    """
    
    db_credential = email_credential.update_email_credential(
        db=db,
        user_id=current_user.id,
        credential_update=credential_update
    )
    
    if not db_credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email configuration not found"
        )
    
    return db_credential


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_email_config(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete email configuration for the current user
    """
    
    success = email_credential.delete_email_credential(db, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email configuration not found"
        )
    
    return None


@router.post("/test", response_model=dict)
def test_email_connection(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Test IMAP connection with current credentials
    """
    
    db_credential = email_credential.get_email_credential(db, current_user.id)
    
    if not db_credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email configuration not found"
        )
    
    # Initialize polling service
    polling_service = EmailPollingService(db, current_user.id)
    
    try:
        # Try to connect
        mail = polling_service.connect_imap()
        
        # Get mailbox list
        status_code, mailbox_list = mail.list()
        mailboxes = [box.decode() for box in mailbox_list] if mailbox_list else []
        
        # Logout
        mail.logout()
        
        return {
            "success": True,
            "message": "Successfully connected to IMAP server! ✓",
            "mailboxes": mailboxes[:10]  # Return first 10 mailboxes
        }
        
    except Exception as e:
        error_message = str(e)
        
        # Provide more helpful error messages
        if "authentication failed" in error_message.lower() or "auth" in error_message.lower():
            error_message = "Authentication failed. Please check your email and password/app password."
        elif "connection" in error_message.lower():
            error_message = f"Connection failed: {error_message}. Check IMAP server and port."
        elif "timeout" in error_message.lower():
            error_message = "Connection timeout. Check your network and firewall settings."
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )


@router.post("/poll-now", response_model=EmailPollingStats)
def trigger_polling(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Manually trigger email polling for the current user
    """
    
    db_credential = email_credential.get_email_credential(db, current_user.id)
    
    if not db_credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email configuration not found"
        )
    
    if not db_credential.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email configuration is inactive"
        )
    
    # Initialize polling service
    polling_service = EmailPollingService(db, current_user.id)
    
    try:
        # Run polling
        stats = polling_service.poll_emails()
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Polling failed: {str(e)}"
        )


@router.get("/logs", response_model=List[EmailProcessingLogSchema])
def get_processing_logs(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    limit: int = 50
):
    """
    Get email processing logs for the current user
    """
    
    logs = email_credential.get_processing_logs(
        db=db,
        user_id=current_user.id,
        limit=limit
    )
    
    return logs


@router.post("/pause", response_model=EmailCredential)
def pause_email_polling(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Pause automatic email polling for the current user
    """
    
    db_credential = email_credential.get_email_credential(db, current_user.id)
    
    if not db_credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email configuration not found"
        )
    
    # Update polling_enabled to False
    update_data = EmailCredentialUpdate(polling_enabled=False)
    db_credential = email_credential.update_email_credential(
        db=db,
        user_id=current_user.id,
        credential_update=update_data
    )
    
    return db_credential


@router.post("/resume", response_model=EmailCredential)
def resume_email_polling(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Resume automatic email polling for the current user
    """
    
    db_credential = email_credential.get_email_credential(db, current_user.id)
    
    if not db_credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email configuration not found"
        )
    
    # Update polling_enabled to True
    update_data = EmailCredentialUpdate(polling_enabled=True)
    db_credential = email_credential.update_email_credential(
        db=db,
        user_id=current_user.id,
        credential_update=update_data
    )
    
    return db_credential


@router.get("/status", response_model=dict)
def get_polling_status(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current email polling status
    """
    
    db_credential = email_credential.get_email_credential(db, current_user.id)
    
    if not db_credential:
        return {
            "configured": False,
            "polling_enabled": False,
            "message": "Email not configured"
        }
    
    return {
        "configured": True,
        "polling_enabled": db_credential.polling_enabled,
        "polling_interval_minutes": db_credential.polling_interval_minutes,
        "last_poll_time": db_credential.last_poll_time,
        "last_poll_status": db_credential.last_poll_status,
        "email_address": db_credential.email_address
    }
