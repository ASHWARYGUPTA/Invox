from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.api.deps import get_current_active_user
from app.schemas.user import User, UserUpdate
from app.services.auth import get_user_by_id
from app.models.user import User as UserModel

router = APIRouter()


@router.get("/me", response_model=User)
def read_users_me(
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Get current user
    """
    return current_user


@router.put("/me", response_model=User)
def update_user_me(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Update current user
    """
    if user_update.name is not None:
        current_user.name = user_update.name #type:ignore
    if user_update.email is not None:
        current_user.email = user_update.email #type:ignore
    if user_update.image is not None:
        current_user.image = user_update.image #type:ignore
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.get("/{user_id}", response_model=User)
def read_user_by_id(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Get user by ID
    """
    user = get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
