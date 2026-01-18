"""
Email credentials model for storing encrypted OAuth tokens and IMAP settings
"""
from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base import Base


class EmailCredential(Base):
    """
    Stores encrypted email authentication credentials for users
    Supports both Gmail OAuth and IMAP authentication
    """
    __tablename__ = "email_credentials"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, unique=True, index=True)
    
    # Email provider info
    email_address = Column(String, nullable=False)
    provider = Column(String, nullable=False, default="gmail")  # gmail, imap, outlook, etc.
    
    # OAuth credentials (for Gmail) - ENCRYPTED
    oauth_token = Column(Text, nullable=True)  # Encrypted JSON with access_token, refresh_token
    oauth_token_expiry = Column(DateTime, nullable=True)
    
    # IMAP credentials (for non-Gmail) - ENCRYPTED
    imap_server = Column(String, nullable=True)  # e.g., imap.gmail.com
    imap_port = Column(Integer, nullable=True, default=993)
    imap_username = Column(String, nullable=True)  # Usually same as email_address
    imap_password = Column(Text, nullable=True)  # ENCRYPTED
    use_ssl = Column(Boolean, nullable=False, default=True)
    
    # Polling settings
    polling_enabled = Column(Boolean, nullable=False, default=False)
    polling_interval_minutes = Column(Integer, nullable=False, default=5)  # Check every 5 minutes
    last_poll_time = Column(DateTime, nullable=True)
    last_poll_status = Column(String, nullable=True)  # success, error, etc.
    
    # Folder/Label settings
    folder_to_watch = Column(String, nullable=False, default="INBOX")  # INBOX, Invoices, etc.
    mark_as_read = Column(Boolean, nullable=False, default=True)  # Mark processed emails as read
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    last_error = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<EmailCredential {self.email_address} - {self.provider}>"


class EmailProcessingLog(Base):
    """
    Logs email processing attempts for debugging and tracking
    """
    __tablename__ = "email_processing_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    email_credential_id = Column(String, nullable=False)
    
    # Email details
    email_message_id = Column(String, nullable=True)  # Unique email ID from server
    email_subject = Column(String, nullable=True)
    email_from = Column(String, nullable=True)
    email_date = Column(DateTime, nullable=True)
    
    # Processing details
    attachments_found = Column(Integer, nullable=False, default=0)
    attachments_processed = Column(Integer, nullable=False, default=0)
    invoices_created = Column(Integer, nullable=False, default=0)
    
    # Status
    status = Column(String, nullable=False)  # success, partial, failed
    error_message = Column(Text, nullable=True)
    
    # Timestamp
    processed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<EmailProcessingLog {self.email_subject} - {self.status}>"
