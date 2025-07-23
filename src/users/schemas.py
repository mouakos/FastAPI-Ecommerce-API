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
    role: Optional[UserRole] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int


class TokenData(BaseModel):
    user_id: str
    role: str

    def get_user_id(self) -> Optional[UUID]:
        """Retrieve the user ID from the token data.

        Returns:
            Optional[UUID]: The user ID if present, otherwise None.
        """
        if not self.user_id:
            return None
        return UUID(self.user_id)


class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=50)
    new_password_confirm: str = Field(..., min_length=6, max_length=50)


class RoleUpdate(BaseModel):
    role: Optional[UserRole] = None
