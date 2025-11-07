# /backend/app/api/endpoints/auth.py
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token
from app.crud import user as crud_user
from app.api import deps

router = APIRouter()

# 1. The endpoint the user's "Login" button clicks
@router.get("/google")
async def auth_google():
    """
    Redirects the user to Google's login page.
    """
    google_client_id = settings.GOOGLE_CLIENT_ID
    redirect_uri = "http://127.0.0.1:8000/api/v1/auth/google/callback"
    
    scope = "openid profile email"
    
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"response_type=code&"
        f"client_id={google_client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={scope}&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    
    return RedirectResponse(url=google_auth_url)


# 2. The endpoint Google redirects the user back to
@router.get("/google/callback")
async def auth_google_callback(code: str, db: Session = Depends(deps.get_db)):
    """
    Handles the callback from Google.
    Exchanges the 'code' for tokens, gets user info, creates/gets our user,
    and returns our own JWT.
    """
    token_url = "https://oauth2.googleapis.com/token"
    client_id = settings.GOOGLE_CLIENT_ID
    client_secret = settings.GOOGLE_CLIENT_SECRET
    redirect_uri = "http://127.0.0.1:8000/api/v1/auth/google/callback"
    
    # 1. Exchange the code for Google's tokens
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            token_url,
            data={
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
        )
    
    token_data = token_response.json()
    if "error" in token_data:
        raise HTTPException(status_code=400, detail=token_data.get("error_description"))
    
    access_token = token_data.get("access_token")
    
    # 2. Get user info from Google
    user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    async with httpx.AsyncClient() as client:
        user_info_response = await client.get(
            user_info_url, headers={"Authorization": f"Bearer {access_token}"}
        )
    
    user_info = user_info_response.json()
    
    # 3. Get or create the user in our database
    db_user = crud_user.get_or_create_user_by_google(db, google_user_info=user_info)
    if not db_user:
        raise HTTPException(status_code=400, detail="Could not create user")
        
    # 4. Create our *own* access token (JWT)
    # The 'sub' (subject) is our own database user ID
    app_access_token = create_access_token(data={"sub": str(db_user.id)})
    
    # 5. Redirect the user back to the *frontend* app
    # We pass our JWT in the URL hash (fragment)
    frontend_redirect_url = f"http://localhost:3000/auth/callback#token={app_access_token}"
    return RedirectResponse(url=frontend_redirect_url)


@router.get("/me")
async def get_current_user_info(current_user = Depends(deps.get_current_user)):
    """
    Get the current authenticated user's information.
    Returns user details including name, email, and profile picture.
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.full_name,
        "picture": current_user.google_picture,
        "is_active": current_user.is_active,
    }