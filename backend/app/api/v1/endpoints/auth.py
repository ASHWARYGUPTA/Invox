from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.db.session import get_db
from app.services.auth import get_or_create_user_from_oauth, get_user_by_email
from app.core.security import create_access_token
from app.schemas.user import User
from app.api.deps import get_current_active_user
from app.models.user import User as UserModel

router = APIRouter()


class OAuthCallbackData(BaseModel):
    """Data received from NextAuth OAuth callback"""
    email: EmailStr
    name: Optional[str] = None
    image: Optional[str] = None
    provider: str
    provider_account_id: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[int] = None
    id_token: Optional[str] = None
    scope: Optional[str] = None
    token_type: Optional[str] = None
    session_state: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User


@router.post("/oauth/callback", response_model=TokenResponse)
def oauth_callback(
    oauth_data: OAuthCallbackData,
    db: Session = Depends(get_db)
):
    """
    Handle OAuth callback from NextAuth
    This endpoint creates or retrieves the user and returns a JWT token
    """
    try:
        # Get or create user from OAuth data
        user = get_or_create_user_from_oauth(
            db=db,
            email=oauth_data.email,
            name=oauth_data.name,
            image=oauth_data.image,
            provider=oauth_data.provider,
            provider_account_id=oauth_data.provider_account_id,
            access_token=oauth_data.access_token,
            refresh_token=oauth_data.refresh_token,
            expires_at=oauth_data.expires_at,
            id_token=oauth_data.id_token,
            scope=oauth_data.scope,
            token_type=oauth_data.token_type,
            session_state=oauth_data.session_state
        )
        
        # Create JWT token
        access_token = create_access_token(
            data={"sub": user.id, "email": user.email}
        )
        
        return TokenResponse(
            access_token=access_token,
            user=User.model_validate(user)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing OAuth callback: {str(e)}"
        )


@router.get("/me", response_model=User)
def get_current_user_info(
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Get current user information
    Requires authentication
    """
    return current_user


class VerifyEmailRequest(BaseModel):
    email: EmailStr


class VerifyEmailResponse(BaseModel):
    exists: bool
    user: Optional[User] = None


@router.post("/verify-email", response_model=VerifyEmailResponse)
def verify_email(
    request: VerifyEmailRequest,
    db: Session = Depends(get_db)
):
    """
    Verify if an email exists in the database
    Used by NextAuth to check if user exists
    """
    user = get_user_by_email(db, email=request.email)
    
    if user:
        return VerifyEmailResponse(
            exists=True,
            user=User.model_validate(user)
        )
    
    return VerifyEmailResponse(exists=False)
