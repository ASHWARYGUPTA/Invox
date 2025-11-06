# /backend/app/crud/user.py
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_google_sub(db: Session, google_sub: str):
    """Finds a user by their unique Google ID."""
    return db.query(User).filter(User.google_sub == google_sub).first()

def create_user(db: Session, user: UserCreate):
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        # We can add more fields here if needed from Google
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_or_create_user_by_google(db: Session, google_user_info: dict):
    """
    Finds a user by their Google 'sub' ID. 
    If they don't exist, create them.
    """
    db_user = get_user_by_google_sub(db, google_sub=google_user_info['sub'])
    if db_user:
        return db_user
    
    # User doesn't exist, check if email is already used
    db_user_by_email = get_user_by_email(db, email=google_user_info['email'])
    if db_user_by_email:
        # User exists, link their Google account
        db_user_by_email.google_sub = google_user_info['sub']
        db_user_by_email.full_name = google_user_info.get('name')
        db_user_by_email.google_picture = google_user_info.get('picture')
        db.commit()
        db.refresh(db_user_by_email)
        return db_user_by_email

    # New user entirely
    new_user = User(
        email=google_user_info['email'],
        full_name=google_user_info.get('name'),
        google_sub=google_user_info['sub'],
        google_picture=google_user_info.get('picture'),
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user