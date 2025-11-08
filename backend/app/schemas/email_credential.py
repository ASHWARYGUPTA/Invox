"""
Pydantic schemas for email credentials and configuration
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class EmailCredentialBase(BaseModel):
    """Base schema for email credentials"""
    email_address: EmailStr
    provider: str = "gmail"  # gmail, imap, outlook
    
    # IMAP settings (for non-Gmail)
    imap_server: Optional[str] = None
    imap_port: Optional[int] = 993
    use_ssl: bool = True
    
    # Polling settings
    polling_enabled: bool = False
    polling_interval_minutes: int = Field(default=5, ge=1, le=60)
    folder_to_watch: str = "INBOX"
    mark_as_read: bool = True


class EmailCredentialCreate(EmailCredentialBase):
    """Schema for creating email credentials"""
    # For OAuth authentication (Gmail)
    oauth_token: Optional[str] = None  # Encrypted OAuth token
    oauth_token_expiry: Optional[datetime] = None
    
    # For IMAP authentication
    imap_username: Optional[str] = None
    imap_password: Optional[str] = None  # Will be encrypted before storage
    
    class Config:
        json_schema_extra = {
            "example": {
                "email_address": "user@gmail.com",
                "provider": "gmail",
                "imap_server": "imap.gmail.com",
                "imap_port": 993,
                "imap_username": "user@gmail.com",
                "imap_password": "app_specific_password",
                "use_ssl": True,
                "polling_enabled": True,
                "polling_interval_minutes": 5,
                "folder_to_watch": "INBOX",
                "mark_as_read": True
            }
        }


class EmailCredentialUpdate(BaseModel):
    """Schema for updating email credentials"""
    email_address: Optional[EmailStr] = None
    provider: Optional[str] = None
    oauth_token: Optional[str] = None  # Encrypted OAuth token (set by Gmail OAuth callback)
    oauth_token_expiry: Optional[datetime] = None
    imap_password: Optional[str] = None  # New password (will be encrypted)
    imap_server: Optional[str] = None
    imap_port: Optional[int] = None
    imap_username: Optional[str] = None
    polling_enabled: Optional[bool] = None
    polling_interval_minutes: Optional[int] = Field(default=None, ge=1, le=60)
    folder_to_watch: Optional[str] = None
    mark_as_read: Optional[bool] = None
    is_active: Optional[bool] = None


class EmailCredential(EmailCredentialBase):
    """Complete email credential schema for response"""
    id: str
    user_id: str
    
    oauth_token_expiry: Optional[datetime] = None
    imap_username: Optional[str] = None
    
    polling_enabled: bool
    last_poll_time: Optional[datetime] = None
    last_poll_status: Optional[str] = None
    
    is_active: bool
    last_error: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime
    
    # Never expose encrypted fields in API responses
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "user-123",
                "email_address": "user@gmail.com",
                "provider": "gmail",
                "polling_enabled": True,
                "polling_interval_minutes": 5,
                "last_poll_time": "2023-11-08T10:00:00",
                "last_poll_status": "success",
                "is_active": True,
                "created_at": "2023-11-08T09:00:00",
                "updated_at": "2023-11-08T10:00:00"
            }
        }


class EmailPollingStats(BaseModel):
    """Statistics from email polling"""
    emails_checked: int
    invoices_created: int
    errors: int
    status: str
    error_message: Optional[str] = None


class EmailProcessingLogSchema(BaseModel):
    """Email processing log schema"""
    id: str
    user_id: str
    email_subject: Optional[str]
    email_from: Optional[str]
    email_date: Optional[datetime]
    attachments_found: int
    attachments_processed: int
    invoices_created: int
    status: str
    error_message: Optional[str]
    processed_at: datetime
    
    class Config:
        from_attributes = True
