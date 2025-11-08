from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.models.user import User, Account, Session as DBSession
from app.schemas.user import UserCreate, AccountCreate, SessionCreate
import uuid


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user"""
    db_user = User(
        id=str(uuid.uuid4()),
        email=user.email,
        name=user.name,
        image=user.image,
        email_verified=datetime.utcnow() if user.email else None
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_account(db: Session, account: AccountCreate) -> Account:
    """Create a new OAuth account"""
    db_account = Account(
        id=str(uuid.uuid4()),
        user_id=account.user_id,
        type=account.type,
        provider=account.provider,
        provider_account_id=account.provider_account_id,
        refresh_token=account.refresh_token,
        access_token=account.access_token,
        expires_at=account.expires_at,
        token_type=account.token_type,
        scope=account.scope,
        id_token=account.id_token,
        session_state=account.session_state
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


def get_account_by_provider(
    db: Session, 
    provider: str, 
    provider_account_id: str
) -> Optional[Account]:
    """Get account by provider and provider account ID"""
    return db.query(Account).filter(
        Account.provider == provider,
        Account.provider_account_id == provider_account_id
    ).first()


def create_session(db: Session, session: SessionCreate) -> DBSession:
    """Create a new session"""
    db_session = DBSession(
        id=str(uuid.uuid4()),
        session_token=session.session_token,
        user_id=session.user_id,
        expires=session.expires
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def get_session_by_token(db: Session, session_token: str) -> Optional[DBSession]:
    """Get session by token"""
    return db.query(DBSession).filter(
        DBSession.session_token == session_token
    ).first()


def delete_session(db: Session, session_token: str) -> bool:
    """Delete a session"""
    session = get_session_by_token(db, session_token)
    if session:
        db.delete(session)
        db.commit()
        return True
    return False


def get_or_create_user_from_oauth(
    db: Session,
    email: str,
    name: Optional[str],
    image: Optional[str],
    provider: str,
    provider_account_id: str,
    access_token: Optional[str] = None,
    refresh_token: Optional[str] = None,
    expires_at: Optional[int] = None,
    id_token: Optional[str] = None,
    scope: Optional[str] = None,
    token_type: Optional[str] = None,
    session_state: Optional[str] = None
) -> User:
    """
    Get or create user from OAuth provider data
    This is the main function to handle OAuth authentication
    """
    # Check if account exists
    account = get_account_by_provider(db, provider, provider_account_id)
    
    if account:
        # Account exists, return the associated user
        user = get_user_by_id(db, account.user_id)  # type: ignore
        
        # Update account tokens
        account.access_token = access_token  # type: ignore
        account.refresh_token = refresh_token  # type: ignore
        account.expires_at = expires_at  # type: ignore
        account.id_token = id_token  # type: ignore
        account.scope = scope  # type: ignore
        account.token_type = token_type  # type: ignore
        account.session_state = session_state  # type: ignore
        account.updated_at = datetime.utcnow()  # type: ignore
        db.commit()
        
        return user
    
    # Check if user exists by email
    user = get_user_by_email(db, email)
    
    if not user:
        # Create new user
        user = create_user(
            db,
            UserCreate(
                email=email,
                name=name,
                image=image
            )
        )
    
    # Create account for this user
    create_account(
        db,
        AccountCreate(
            user_id=user.id,  # type: ignore
            type="oauth",
            provider=provider,
            provider_account_id=provider_account_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            id_token=id_token,
            scope=scope,
            token_type=token_type,
            session_state=session_state
        )
    )
    
    return user
