from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime, date
from uuid import UUID, uuid4
from app.utils.date_time_provider import get_utc_now

from app.models.cart import Cart
from app.models.order import Order

if TYPE_CHECKING:
    from app.models.review import Review
    from app.models.address import Address
    from app.models.wishlist import Wishlist


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(index=True, nullable=False, unique=True)
    password_hash: str = Field(nullable=False, exclude=True)
    full_name: str = Field(nullable=False)
    gender: Optional[str] = Field(default="other", nullable=True)
    date_of_birth: Optional[date] = Field(default=None, nullable=True)
    phone_number: Optional[str] = Field(default=None, nullable=True)
    role: Optional[str] = Field(default="customer", nullable=False)
    is_active: bool = Field(default=True, nullable=False)

    created_at: datetime = Field(default_factory=get_utc_now, nullable=False)
    updated_at: datetime = Field(default_factory=get_utc_now, nullable=False)

    # Relationship with addresses - one-to-many
    addresses: list["Address"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )

    # Relationship with reviews - one-to-many
    reviews: list["Review"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )

    # Relationship with cart - one-to-one
    cart: Optional["Cart"] = Relationship(back_populates="user")

    # Relationship with orders - one-to-many
    orders: list["Order"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )

    # Relationship with wishlist - one-to-one
    wishlist: Optional["Wishlist"] = Relationship(back_populates="user")
