# /backend/app/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core import security
from app.crud import user as crud_user
from app.models.user import User

# This tells FastAPI where to look for the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token") # We don't have this, but it's needed for setup

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ADD THIS NEW FUNCTION ---
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Decodes the JWT token from the 'Authorization' header
    and returns the corresponding user from the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    user_id = security.decode_access_token(token)
    if user_id is None:
        raise credentials_exception
    
    user = crud_user.get_user(db, user_id=int(user_id))
    if user is None:
        raise credentials_exception
    
    return user