from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from enum import Enum
from uuid import UUID


class Gender(str, Enum):
    male = "male"
    female = "female"
    other = "other"


class UserRole(str, Enum):
    customer = "customer"
    admin = "admin"


class UserBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr = Field(..., max_length=50)
    gender: Gender


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=50)


class UserRead(UserBase):
    id: UUID
    is_active: bool
    date_of_birth: Optional[datetime] = None
    phone_number: Optional[str] = None
    role: UserRole
    created_at: datetime


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
