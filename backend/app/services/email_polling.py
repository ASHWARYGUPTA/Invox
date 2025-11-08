"""
Email polling service using IMAP for reading emails and extracting invoices
Supports Gmail OAuth and standard IMAP authentication
"""
import imaplib
import email
from email.header import decode_header
import json
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.email_credential import EmailCredential, EmailProcessingLog
from app.services.encryption import encryption_service
from app.services.invoice_processing import process_invoice_file
from app.crud.invoice import create_invoice
from app.schemas.invoice import InvoiceCreate
import base64


class EmailPollingService:
    """
    Service for polling emails via IMAP or Gmail API (OAuth)
    Automatically detects provider and uses appropriate method
    """
    
    SUPPORTED_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png', '.txt']
    SUPPORTED_MIME_TYPES = [
        'application/pdf',
        'image/jpeg',
        'image/jpg',
        'image/png',
        'text/plain'
    ]
    
    def __init__(self, db: Session, user_id: str):
        """
        Initialize email polling service
        
        Args:
            db: Database session
            user_id: User ID to fetch email credentials for
        """
        self.db = db
        
        # Import here to avoid circular dependency
        from app.crud import email_credential as email_crud
        
        # Fetch email credential from database
        self.email_credential = email_crud.get_email_credential(db, user_id)
        
        if not self.email_credential:
            raise ValueError(f"No email credentials found for user {user_id}")
        
        self.mail = None
        self.gmail_service = None
        self.is_gmail_oauth = self._is_gmail_with_oauth()
    
    def _is_gmail_with_oauth(self) -> bool:
        """
        Check if this is a Gmail account using OAuth
        
        Returns:
            True if Gmail with OAuth, False otherwise
        """
        is_gmail = self.email_credential.provider == "gmail"
        has_oauth = self.email_credential.oauth_token is not None
        
        # Debug logging
        if is_gmail and not has_oauth:
            print(f"⚠️  Gmail account detected but OAuth token is NULL for {self.email_credential.email_address}")
            print(f"    Please complete Gmail OAuth authentication flow")
        elif is_gmail and has_oauth:
            print(f"✅ Gmail OAuth detected for {self.email_credential.email_address}")
        else:
            print(f"ℹ️  Non-Gmail provider detected: {self.email_credential.provider}")
        
        return is_gmail and has_oauth
    
    def connect(self) -> bool:
        """
        Connect to email service (Gmail OAuth or IMAP)
        
        Returns:
            True if connection successful, False otherwise
        """
        if self.is_gmail_oauth:
            return self.connect_gmail_oauth()
        else:
            return self.connect_imap()
    
    def connect_gmail_oauth(self) -> bool:
        """
        Connect to Gmail using OAuth
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            from app.services.gmail_oauth import GmailOAuthService
            
            gmail_oauth = GmailOAuthService(self.db, self.email_credential)
            if gmail_oauth.connect():
                self.gmail_service = gmail_oauth
                print(f"✅ Connected to Gmail OAuth: {self.email_credential.email_address}")
                return True
            return False
            
        except Exception as e:
            print(f"❌ Gmail OAuth connection failed: {e}")
            return False
    
    def connect_imap(self) -> bool:
        """
        Connect to IMAP server using stored credentials
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Decrypt IMAP password
            if not self.email_credential.imap_password:
                raise ValueError("No IMAP password stored")
            
            password = encryption_service.decrypt(self.email_credential.imap_password)
            
            # Connect to IMAP server
            if self.email_credential.use_ssl:
                self.mail = imaplib.IMAP4_SSL(
                    self.email_credential.imap_server,
                    self.email_credential.imap_port
                )
            else:
                self.mail = imaplib.IMAP4(
                    self.email_credential.imap_server,
                    self.email_credential.imap_port
                )
            
            # Login
            username = self.email_credential.imap_username or self.email_credential.email_address
            self.mail.login(username, password)
            
            print(f"✅ Connected to IMAP: {self.email_credential.email_address}")
            return True
            
        except Exception as e:
            print(f"❌ IMAP connection failed: {e}")
            self.email_credential.last_error = str(e)
            self.email_credential.last_poll_status = "error"
            self.db.commit()
            return False
    
    def disconnect(self):
        """Close IMAP connection"""
        if self.mail:
            try:
                self.mail.close()
                self.mail.logout()
            except:
                pass
    
    def decode_email_subject(self, subject: str) -> str:
        """Decode email subject handling different encodings"""
        try:
            decoded_parts = decode_header(subject)
            decoded_subject = ""
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    decoded_subject += part.decode(encoding or 'utf-8', errors='ignore')
                else:
                    decoded_subject += part
            return decoded_subject
        except:
            return subject
    
    def get_unread_emails(self) -> List[str]:
        """
        Get list of unread email IDs from configured folder
        
        Returns:
            List of email message IDs
        """
        try:
            # Select folder
            folder = self.email_credential.folder_to_watch or "INBOX"
            self.mail.select(folder)
            
            # Search for unread messages
            status, messages = self.mail.search(None, 'UNSEEN')
            
            if status != 'OK':
                return []
            
            # Get message IDs (limit to last 5)
            all_message_ids = messages[0].split()
            # Get only the last 5 messages (most recent)
            message_ids = all_message_ids[-5:] if len(all_message_ids) > 5 else all_message_ids
            
            print(f"📧 Found {len(all_message_ids)} unread email(s) in {folder}, checking last {len(message_ids)}")
            
            return [msg_id.decode() for msg_id in message_ids]
            
        except Exception as e:
            print(f"❌ Error fetching unread emails: {e}")
            return []
    
    def fetch_email(self, message_id: str) -> Optional[email.message.Message]:
        """
        Fetch full email message by ID
        
        Args:
            message_id: Email message ID
        
        Returns:
            Email message object or None
        """
        try:
            status, msg_data = self.mail.fetch(message_id, '(RFC822)')
            
            if status != 'OK':
                return None
            
            # Parse email
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            return email_message
            
        except Exception as e:
            print(f"❌ Error fetching email {message_id}: {e}")
            return None
    
    def extract_attachments(self, email_message: email.message.Message) -> List[Tuple[str, bytes, str]]:
        """
        Extract attachments from email
        
        Args:
            email_message: Email message object
        
        Returns:
            List of tuples (filename, file_bytes, content_type)
        """
        attachments = []
        
        for part in email_message.walk():
            # Check if this part is an attachment
            if part.get_content_maintype() == 'multipart':
                continue
            
            if part.get('Content-Disposition') is None:
                continue
            
            filename = part.get_filename()
            
            if not filename:
                continue
            
            # Decode filename
            filename = self.decode_email_subject(filename)
            
            # Check if file type is supported
            file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
            if f'.{file_ext}' not in self.SUPPORTED_EXTENSIONS:
                print(f"  ⏭️  Skipping unsupported file: {filename}")
                continue
            
            # Get file content
            file_data = part.get_payload(decode=True)
            content_type = part.get_content_type()
            
            print(f"  📎 Found attachment: {filename} ({content_type})")
            attachments.append((filename, file_data, content_type))
        
        return attachments
    
    def process_attachment(self, filename: str, file_bytes: bytes, content_type: str, user_id: str) -> bool:
        """
        Process invoice attachment using Gemini AI
        
        Args:
            filename: Original filename
            file_bytes: File content as bytes
            content_type: MIME type
            user_id: User ID who owns this email account
        
        Returns:
            True if processed successfully, False otherwise
        """
        try:
            print(f"  🤖 Processing {filename} with Gemini AI...")
            
            # Map content types
            if content_type == 'text/plain':
                content_type = 'text/plain'
            elif 'image' in content_type:
                if not content_type.startswith('image/'):
                    content_type = 'image/jpeg'  # Default for images
            
            # Process with Gemini AI
            extraction_result = process_invoice_file(file_bytes, content_type)
            
            # Get file size and type
            file_size = len(file_bytes)
            file_type = filename.split('.')[-1].lower() if '.' in filename else 'unknown'
            
            # Create invoice in database
            invoice_data = InvoiceCreate(
                original_filename=filename,
                file_size=file_size,
                file_type=file_type
            )
            
            # Extract text for searchability (if PDF)
            extracted_text = None
            if content_type == 'application/pdf':
                from app.services.invoice_processing import extract_text_from_pdf
                extracted_text = extract_text_from_pdf(file_bytes)
            
            invoice = create_invoice(
                db=self.db,
                user_id=user_id,
                invoice_data=invoice_data,
                extraction_result=extraction_result,
                extracted_text=extracted_text
            )
            
            print(f"  ✅ Invoice created: {invoice.id} - {invoice.vendor_name}")
            return True
            
        except Exception as e:
            print(f"  ❌ Error processing attachment: {e}")
            return False
    
    def mark_as_read(self, message_id: str):
        """Mark email as read"""
        try:
            self.mail.store(message_id, '+FLAGS', '\\Seen')
        except Exception as e:
            print(f"⚠️ Could not mark email as read: {e}")
    
    def process_single_email(self, message_id: str) -> EmailProcessingLog:
        """
        Process a single email and its attachments
        
        Args:
            message_id: Email message ID
        
        Returns:
            EmailProcessingLog entry
        """
        
        # Check if this message has already been processed
        existing_log = self.db.query(EmailProcessingLog).filter(
            EmailProcessingLog.user_id == self.email_credential.user_id,
            EmailProcessingLog.email_message_id == message_id,
            EmailProcessingLog.status == "success"
        ).first()
        
        if existing_log:
            print(f"⏭️  Skipping already processed email: {message_id}")
            log = EmailProcessingLog(
                user_id=self.email_credential.user_id,
                email_credential_id=self.email_credential.id,
                email_message_id=message_id,
                status="skipped",
                error_message="Already processed"
            )
            return log
        
        log = EmailProcessingLog(
            user_id=self.email_credential.user_id,
            email_credential_id=self.email_credential.id,
            email_message_id=message_id,
            status="processing",
            attachments_found=0,
            attachments_processed=0,
            invoices_created=0
        )
        
        try:
            # Fetch email
            email_message = self.fetch_email(message_id)
            
            if not email_message:
                log.status = "failed"
                log.error_message = "Could not fetch email"
                return log
            
            # Extract email metadata
            subject = email_message.get('Subject', 'No Subject')
            from_addr = email_message.get('From', 'Unknown')
            date_str = email_message.get('Date')
            
            log.email_subject = self.decode_email_subject(subject)
            log.email_from = from_addr
            
            try:
                log.email_date = email.utils.parsedate_to_datetime(date_str)
            except:
                log.email_date = datetime.utcnow()
            
            print(f"\n📨 Processing: {log.email_subject}")
            print(f"   From: {from_addr}")
            
            # Extract attachments
            attachments = self.extract_attachments(email_message)
            log.attachments_found = len(attachments)
            
            if not attachments:
                print("  ℹ️ No supported attachments found")
                log.status = "success"
                log.error_message = "No attachments"
                return log
            
            # Process each attachment
            invoices_created = 0
            for filename, file_bytes, content_type in attachments:
                if self.process_attachment(filename, file_bytes, content_type, self.email_credential.user_id):
                    log.attachments_processed += 1
                    invoices_created += 1
            
            log.invoices_created = invoices_created
            
            # Determine status
            if log.attachments_processed == log.attachments_found:
                log.status = "success"
            elif log.attachments_processed > 0:
                log.status = "partial"
                log.error_message = f"Processed {log.attachments_processed}/{log.attachments_found} attachments"
            else:
                log.status = "failed"
                log.error_message = "No attachments could be processed"
            
            # Mark as read if configured
            if self.email_credential.mark_as_read and log.status in ["success", "partial"]:
                self.mark_as_read(message_id)
                print("  ✓ Marked as read")
            
        except Exception as e:
            print(f"❌ Error processing email: {e}")
            log.status = "failed"
            log.error_message = str(e)
        
        return log
    
    def poll_emails(self) -> dict:
        """
        Main function to poll emails and process invoices
        
        Returns:
            Dictionary with processing statistics
        """
        stats = {
            "emails_checked": 0,
            "invoices_created": 0,
            "errors": 0,
            "status": "unknown"
        }
        
        try:
            # Connect to email service (Gmail OAuth or IMAP)
            if not self.connect():
                stats["status"] = "connection_failed"
                return stats
            
            # Get unread emails based on provider type
            if self.is_gmail_oauth:
                return self.poll_gmail_oauth(stats)
            else:
                return self.poll_imap(stats)
            
        except Exception as e:
            print(f"❌ Polling error: {e}")
            stats["status"] = "error"
            stats["error_message"] = str(e)
            
            self.email_credential.last_poll_status = "error"
            self.email_credential.last_error = str(e)
            self.db.commit()
            
            return stats
        
        finally:
            self.disconnect()
    
    def poll_imap(self, stats: dict) -> dict:
        """
        Poll emails using IMAP
        
        Args:
            stats: Statistics dictionary to update
            
        Returns:
            Updated statistics dictionary
        """
        try:
            # Get unread emails
            message_ids = self.get_unread_emails()
            stats["emails_checked"] = len(message_ids)
            
            if not message_ids:
                print("📭 No new emails found")
                stats["status"] = "no_emails"
                self.email_credential.last_poll_status = "success"
                self.email_credential.last_poll_time = datetime.utcnow()
                self.db.commit()
                return stats
            
            # Process each email
            for message_id in message_ids:
                log = self.process_single_email(message_id)
                
                # Only save log if not skipped (skipped means already processed)
                if log.status != "skipped":
                    # Save log to database
                    self.db.add(log)
                    self.db.commit()
                    
                    stats["invoices_created"] += log.invoices_created
                    if log.status == "failed":
                        stats["errors"] += 1
                else:
                    print(f"  ⏭️  Skipped duplicate email")

            
            # Update credential status
            self.email_credential.last_poll_time = datetime.utcnow()
            self.email_credential.last_poll_status = "success"
            self.email_credential.last_error = None
            self.db.commit()
            
            stats["status"] = "success"
            print(f"\n✅ Polling complete: {stats['invoices_created']} invoices created")
            
        except Exception as e:
            print(f"❌ Polling error: {e}")
            stats["status"] = "error"
            stats["error_message"] = str(e)
            
            self.email_credential.last_poll_status = "error"
            self.email_credential.last_error = str(e)
            self.db.commit()
        
        return stats
    
    def poll_gmail_oauth(self, stats: dict) -> dict:
        """
        Poll emails using Gmail OAuth/API
        
        Args:
            stats: Statistics dictionary to update
            
        Returns:
            Updated statistics dictionary
        """
        try:
            if not self.gmail_service:
                stats["status"] = "connection_failed"
                return stats
            
            # Get last 5 unread messages from Gmail API
            messages = self.gmail_service.get_unread_messages(max_results=5)
            stats["emails_checked"] = len(messages)
            
            if not messages:
                print("📭 No new emails found")
                stats["status"] = "no_emails"
                self.email_credential.last_poll_status = "success"
                self.email_credential.last_poll_time = datetime.utcnow()
                self.db.commit()
                return stats
            
            print(f"📧 Found {len(messages)} unread email(s)")
            
            # Process each message
            for message_data in messages:
                log = self.process_gmail_message(message_data)
                
                # Only save log if not skipped (skipped means already processed)
                if log.status != "skipped":
                    # Save log to database
                    self.db.add(log)
                    self.db.commit()
                    
                    stats["invoices_created"] += log.invoices_created
                    if log.status == "failed":
                        stats["errors"] += 1
                else:
                    print(f"  ⏭️  Skipped duplicate email")

            
            # Update credential status
            self.email_credential.last_poll_time = datetime.utcnow()
            self.email_credential.last_poll_status = "success"
            self.email_credential.last_error = None
            self.db.commit()
            
            stats["status"] = "success"
            print(f"\n✅ Polling complete: {stats['invoices_created']} invoices created")
            
        except Exception as e:
            print(f"❌ Gmail OAuth polling error: {e}")
            stats["status"] = "error"
            stats["error_message"] = str(e)
            
            self.email_credential.last_poll_status = "error"
            self.email_credential.last_error = str(e)
            self.db.commit()
        
        return stats
    
    def process_gmail_message(self, message_data: dict) -> EmailProcessingLog:
        """
        Process a single Gmail message and its attachments
        
        Args:
            message_data: Full Gmail message data from API
            
        Returns:
            EmailProcessingLog entry
        """
        # Extract message details
        details = self.gmail_service.get_message_details(message_data)
        message_id = details['id']
        email_message_id = details.get('message_id', message_id)
        
        # Check if this message has already been processed
        existing_log = self.db.query(EmailProcessingLog).filter(
            EmailProcessingLog.user_id == self.email_credential.user_id,
            EmailProcessingLog.email_message_id == email_message_id,
            EmailProcessingLog.status == "success"
        ).first()
        
        if existing_log:
            print(f"⏭️  Skipping already processed email: {email_message_id}")
            log = EmailProcessingLog(
                user_id=self.email_credential.user_id,
                email_credential_id=self.email_credential.id,
                email_message_id=email_message_id,
                status="skipped",
                error_message="Already processed"
            )
            return log
        
        log = EmailProcessingLog(
            user_id=self.email_credential.user_id,
            email_credential_id=self.email_credential.id,
            email_message_id=email_message_id,
            status="processing",
            attachments_found=0,
            attachments_processed=0,
            invoices_created=0
        )
        
        try:
            log.email_subject = details['subject']
            log.email_from = details['from']
            
            try:
                import email.utils
                log.email_date = email.utils.parsedate_to_datetime(details['date'])
            except:
                log.email_date = datetime.utcnow()
            
            print(f"\n📨 Processing: {log.email_subject}")
            print(f"   From: {details['from']}")
            
            # Get attachments from Gmail API
            attachments = self.gmail_service.get_message_attachments(message_id)
            log.attachments_found = len(attachments)
            
            if not attachments:
                print("  ℹ️ No attachments found")
                log.status = "success"
                log.error_message = "No attachments"
                return log
            
            # Filter supported attachments
            supported_attachments = []
            for filename, file_bytes in attachments:
                file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
                if f'.{file_ext}' in self.SUPPORTED_EXTENSIONS:
                    supported_attachments.append((filename, file_bytes))
                    print(f"  📎 Found attachment: {filename}")
                else:
                    print(f"  ⏭️  Skipping unsupported file: {filename}")
            
            log.attachments_found = len(supported_attachments)
            
            if not supported_attachments:
                print("  ℹ️ No supported attachments found")
                log.status = "success"
                log.error_message = "No supported attachments"
                return log
            
            # Process each supported attachment
            invoices_created = 0
            for filename, file_bytes in supported_attachments:
                # Determine content type from extension
                file_ext = filename.lower().split('.')[-1]
                content_type_map = {
                    'pdf': 'application/pdf',
                    'jpg': 'image/jpeg',
                    'jpeg': 'image/jpeg',
                    'png': 'image/png',
                    'txt': 'text/plain'
                }
                content_type = content_type_map.get(file_ext, 'application/octet-stream')
                
                if self.process_attachment(filename, file_bytes, content_type, self.email_credential.user_id):
                    log.attachments_processed += 1
                    invoices_created += 1
            
            log.invoices_created = invoices_created
            
            # Determine status
            if log.attachments_processed == log.attachments_found:
                log.status = "success"
            elif log.attachments_processed > 0:
                log.status = "partial"
                log.error_message = f"Processed {log.attachments_processed}/{log.attachments_found} attachments"
            else:
                log.status = "failed"
                log.error_message = "No attachments could be processed"
            
            # Mark as read if configured
            if self.email_credential.mark_as_read and log.status in ["success", "partial"]:
                self.gmail_service.mark_as_read(message_id)
                print("  ✓ Marked as read")
            
        except Exception as e:
            print(f"❌ Error processing Gmail message: {e}")
            log.status = "failed"
            log.error_message = str(e)
        
        return log
