from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    role: str = "user"

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserInDB(UserResponse):
    password_hash: str