"""
Background worker for automated email polling
"""
import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.crud import email_credential as email_crud
from app.services.email_polling import EmailPollingService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmailPollerWorker:
    """
    Background worker that polls emails for all active users
    """
    
    def __init__(self, check_interval_seconds: int = 60):
        """
        Initialize worker
        
        Args:
            check_interval_seconds: How often to check for users to poll (default 60s)
        """
        self.check_interval_seconds = check_interval_seconds
        self.running = False
        
    def get_db(self) -> Session:
        """Get database session"""
        return SessionLocal()
        
    async def poll_user_emails(self, user_id: str, db: Session) -> None:
        """
        Poll emails for a single user
        
        Args:
            user_id: User ID
            db: Database session
        """
        try:
            logger.info(f"Starting email poll for user {user_id}")
            
            # Initialize polling service
            polling_service = EmailPollingService(db, user_id)
            
            # Run polling (this is synchronous)
            stats = await asyncio.to_thread(polling_service.poll_emails)
            
            logger.info(
                f"Completed email poll for user {user_id}: "
                f"{stats.get('emails_checked', 0)} emails checked, "
                f"{stats.get('invoices_created', 0)} invoices created, "
                f"status: {stats.get('status', 'unknown')}"
            )
            
        except Exception as e:
            logger.error(f"Error polling emails for user {user_id}: {str(e)}")
            
    async def process_user(self, user_id: str, credential_id: int) -> None:
        """
        Process a single user's emails
        
        Args:
            user_id: User ID
            credential_id: Email credential ID
        """
        db = self.get_db()
        try:
            # Check if user should be polled
            credential = db.query(email_crud.EmailCredential).filter(
                email_crud.EmailCredential.id == credential_id
            ).first()
            
            if not credential:
                logger.warning(f"Credential {credential_id} not found")
                return
                
            # Check if enough time has passed since last poll
            now = datetime.utcnow()
            next_poll_time = None
            
            if credential.last_poll_time:
                next_poll_time = credential.last_poll_time + timedelta(
                    minutes=credential.polling_interval_minutes
                )
                
            # Skip if not ready to poll yet
            if next_poll_time and now < next_poll_time:
                logger.debug(
                    f"Skipping user {user_id}, next poll at {next_poll_time}"
                )
                return
                
            # Poll emails
            await self.poll_user_emails(user_id, db)
            
        finally:
            db.close()
            
    async def run_polling_cycle(self) -> None:
        """
        Run one cycle of polling for all active users
        """
        db = self.get_db()
        try:
            # Get all active credentials
            credentials = email_crud.get_all_active_credentials(db)
            
            logger.info(f"Found {len(credentials)} active email configurations")
            
            # Process each user
            tasks = []
            for cred in credentials:
                task = asyncio.create_task(
                    self.process_user(cred.user_id, cred.id)
                )
                tasks.append(task)
                
            # Wait for all tasks to complete
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
                
        except Exception as e:
            logger.error(f"Error in polling cycle: {str(e)}")
        finally:
            db.close()
            
    async def start(self) -> None:
        """
        Start the background worker
        """
        self.running = True
        logger.info(
            f"Starting email poller worker (check interval: {self.check_interval_seconds}s)"
        )
        
        while self.running:
            try:
                await self.run_polling_cycle()
                
                # Wait before next cycle
                await asyncio.sleep(self.check_interval_seconds)
                
            except Exception as e:
                logger.error(f"Unexpected error in worker: {str(e)}")
                await asyncio.sleep(self.check_interval_seconds)
                
    def stop(self) -> None:
        """
        Stop the background worker
        """
        logger.info("Stopping email poller worker")
        self.running = False


# Global worker instance
_worker = None


def get_worker() -> EmailPollerWorker:
    """Get or create worker instance"""
    global _worker
    if _worker is None:
        _worker = EmailPollerWorker()
    return _worker


async def start_background_polling():
    """
    Start background email polling
    Call this from FastAPI startup event
    """
    worker = get_worker()
    await worker.start()


def stop_background_polling():
    """
    Stop background email polling
    Call this from FastAPI shutdown event
    """
    worker = get_worker()
    worker.stop()


if __name__ == "__main__":
    # Run standalone worker
    logger.info("Starting standalone email poller worker")
    worker = EmailPollerWorker(check_interval_seconds=60)
    asyncio.run(worker.start())
