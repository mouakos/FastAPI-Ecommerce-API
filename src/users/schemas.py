from datetime import date, datetime
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
    full_name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr = Field(..., max_length=50)
    gender: Gender


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=50)


class UserRead(UserBase):
    id: UUID
    date_of_birth: Optional[datetime] = None
    phone_number: Optional[str] = None
    role: UserRole
    created_at: datetime


class AccountUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=50)
    date_of_birth: Optional[date] = Field(None)
    phone_number: Optional[str] = Field(None, max_length=15)


class UserUpdate(AccountUpdate):
    pass


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"
    access_token_expires_in: int


class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=50)
    new_password_confirm: str = Field(..., min_length=6, max_length=50)


class RoleUpdate(BaseModel):
    role: Optional[UserRole] = None
