# /backend/app/schemas/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    pass  # We'll add password here if we do email/pass login

class User(UserBase):
    id: int
    is_active: bool
    google_picture: Optional[str] = None

    class Config:
        from_attributes = True # Replaced orm_mode