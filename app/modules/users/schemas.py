from datetime import date, datetime
from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID

from ..addresses.schemas import AddressRead
from ..orders.schemas import OrderRead
from ..reviews.schemas import ReviewRead
from ..wishlist.schemas import WishlistRead


class UserBase(BaseModel):
    full_name: str = Field(
        ..., min_length=2, max_length=50, description="Full name of the user"
    )
    email: EmailStr = Field(..., max_length=50, description="Email address of the user")
    gender: Literal["male", "female", "other"] = Field(
        default="other", description="Gender of the user"
    )


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
    role: Literal["customer", "admin"] = Field(..., description="Role of the user")
    gender: Literal["male", "female", "other"] = Field(
        ..., description="Gender of the user"
    )
    is_active: bool = Field(
        default=True, description="Indicates if the user account is active"
    )
    created_at: datetime = Field(..., description="Timestamp when the user was created")
    updated_at: datetime = Field(
        ..., description="Timestamp when the user was last updated"
    )


class UserReadDetail(UserRead):
    addresses: Optional[list[AddressRead]] = Field(
        default_factory=list, description="List of addresses associated with the user"
    )
    orders: Optional[list[OrderRead]] = Field(
        default_factory=list, description="List of orders associated with the user"
    )
    reviews: Optional[list[ReviewRead]] = Field(
        default_factory=list, description="List of reviews associated with the user"
    )
    wishlist: Optional["WishlistRead"] = Field(
        default=None, description="Wishlist associated with the user"
    )


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(
        None, min_length=2, max_length=50, description="Full name of the user"
    )
    date_of_birth: Optional[date] = Field(None, description="Date of birth of the user")
    phone_number: Optional[str] = Field(
        None, max_length=15, description="Phone number of the user"
    )
    gender: Optional[Literal["male", "female", "other"]] = Field(
        default="other", description="Gender of the user"
    )


class AdminUserUpdate(UserUpdate):
    role: Optional[Literal["customer", "admin"]] = Field(None, description="Role of the user")
    is_active: Optional[bool] = Field(
        None, description="Indicates if the user account is active"
    )


class PasswordUpdate(BaseModel):
    current_password: str = Field(..., description="Current password of the user")
    new_password: str = Field(
        ..., min_length=6, max_length=50, description="New password of the user"
    )
    new_password_confirm: str = Field(
        ..., min_length=6, max_length=50, description="Confirm new password of the user"
    )
