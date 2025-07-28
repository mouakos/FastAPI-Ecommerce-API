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
    full_name: str = Field(
        ..., min_length=2, max_length=50, description="Full name of the user"
    )
    email: EmailStr = Field(..., max_length=50, description="Email address of the user")
    gender: Gender = Field(..., description="Gender of the user")


class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=6,
        max_length=50,
        exclude=True,
        repr=False,
        description="Password for the user account",
    )


class UserRead(UserBase):
    id: UUID = Field(..., description="Unique identifier for the user")
    date_of_birth: Optional[date] = Field(None, description="Date of birth of the user")
    phone_number: Optional[str] = Field(None, description="Phone number of the user")
    role: UserRole = Field(default=UserRole.customer, description="Role of the user")
    is_active: bool = Field(
        default=True, description="Indicates if the user account is active"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the user was created",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the user was last updated",
    )


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(
        None, min_length=2, max_length=50, description="Full name of the user"
    )
    date_of_birth: Optional[date] = Field(None, description="Date of birth of the user")
    phone_number: Optional[str] = Field(
        None, max_length=15, description="Phone number of the user"
    )


class AdminUserUpdate(UserUpdate):
    role: Optional[UserRole] = Field(None, description="Role of the user")
    is_active: Optional[bool] = Field(
        None, description="Indicates if the user account is active"
    )


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    refresh_token: Optional[str] = Field(
        None, description="JWT refresh token, if applicable"
    )
    token_type: str = Field(default="Bearer", description="Type of the token")
    access_token_expires_in: int = Field(
        default=3600, description="Access token expiration time in seconds"
    )


class PasswordUpdate(BaseModel):
    current_password: str = Field(..., description="Current password of the user")
    new_password: str = Field(
        ..., min_length=6, max_length=50, description="New password of the user"
    )
    new_password_confirm: str = Field(
        ..., min_length=6, max_length=50, description="Confirm new password of the user"
    )
