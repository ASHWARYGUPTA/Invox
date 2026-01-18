"""
CRUD operations for email credentials
"""
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.models.email_credential import EmailCredential, EmailProcessingLog
from app.schemas.email_credential import EmailCredentialCreate, EmailCredentialUpdate
from app.services.encryption import encryption_service


def create_email_credential(
    db: Session,
    user_id: str,
    credential_data: EmailCredentialCreate
) -> EmailCredential:
    """
    Create email credentials for a user (encrypts sensitive data)
    
    Args:
        db: Database session
        user_id: User ID
        credential_data: Email credential data
    
    Returns:
        Created EmailCredential
    """
    
    # Encrypt IMAP password if provided
    encrypted_password = None
    if credential_data.imap_password:
        encrypted_password = encryption_service.encrypt(credential_data.imap_password)
    
    db_credential = EmailCredential(
        user_id=user_id,
        email_address=credential_data.email_address,
        provider=credential_data.provider,
        oauth_token=credential_data.oauth_token,  # Already encrypted by OAuth callback
        oauth_token_expiry=credential_data.oauth_token_expiry,
        imap_server=credential_data.imap_server,
        imap_port=credential_data.imap_port,
        imap_username=credential_data.imap_username or credential_data.email_address,
        imap_password=encrypted_password,
        use_ssl=credential_data.use_ssl,
        polling_enabled=credential_data.polling_enabled,
        polling_interval_minutes=credential_data.polling_interval_minutes,
        folder_to_watch=credential_data.folder_to_watch,
        mark_as_read=credential_data.mark_as_read
    )
    
    db.add(db_credential)
    db.commit()
    db.refresh(db_credential)
    
    print(f"✅ Created email credential for {credential_data.email_address}")
    return db_credential


def get_email_credential(db: Session, user_id: str) -> Optional[EmailCredential]:
    """
    Get email credentials for a user
    
    Args:
        db: Database session
        user_id: User ID
    
    Returns:
        EmailCredential or None
    """
    return db.query(EmailCredential).filter(
        EmailCredential.user_id == user_id
    ).first()


def update_email_credential(
    db: Session,
    user_id: str,
    credential_update: EmailCredentialUpdate
) -> Optional[EmailCredential]:
    """
    Update email credentials
    
    Args:
        db: Database session
        user_id: User ID
        credential_update: Fields to update
    
    Returns:
        Updated EmailCredential or None
    """
    
    db_credential = get_email_credential(db, user_id)
    
    if not db_credential:
        return None
    
    # Update fields
    update_data = credential_update.model_dump(exclude_unset=True)
    
    # Encrypt password if provided
    if 'imap_password' in update_data and update_data['imap_password']:
        update_data['imap_password'] = encryption_service.encrypt(update_data['imap_password'])
    
    for field, value in update_data.items():
        setattr(db_credential, field, value)
    
    db_credential.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_credential)
    
    print(f"✅ Updated email credential for user {user_id}")
    return db_credential


def delete_email_credential(db: Session, user_id: str) -> bool:
    """
    Delete email credentials
    
    Args:
        db: Database session
        user_id: User ID
    
    Returns:
        True if deleted, False if not found
    """
    
    db_credential = get_email_credential(db, user_id)
    
    if not db_credential:
        return False
    
    db.delete(db_credential)
    db.commit()
    
    print(f"✅ Deleted email credential for user {user_id}")
    return True


def get_all_active_credentials(db: Session) -> list[EmailCredential]:
    """
    Get all active email credentials for polling
    
    Args:
        db: Database session
    
    Returns:
        List of active EmailCredentials
    """
    return db.query(EmailCredential).filter(
        EmailCredential.is_active == True,
        EmailCredential.polling_enabled == True
    ).all()


def get_processing_logs(
    db: Session,
    user_id: str,
    limit: int = 50
) -> list[EmailProcessingLog]:
    """
    Get email processing logs for a user
    
    Args:
        db: Database session
        user_id: User ID
        limit: Maximum number of logs to return
    
    Returns:
        List of EmailProcessingLogs
    """
    return db.query(EmailProcessingLog).filter(
        EmailProcessingLog.user_id == user_id
    ).order_by(
        EmailProcessingLog.processed_at.desc()
    ).limit(limit).all()
