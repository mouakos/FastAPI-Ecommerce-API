from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from datetime import date
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from .review import Review
    from .address import Address
    from .wishlist import Wishlist
    from .cart import Cart
    from .order import Order


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(index=True, nullable=False, unique=True)
    password_hash: str = Field(nullable=False, exclude=True)
    fistname: Optional[str] = Field(default=None, nullable=True)
    lastname: Optional[str] = Field(default=None, nullable=True)
    gender: Optional[str] = Field(default="other", nullable=True)
    date_of_birth: Optional[date] = Field(default=None, nullable=True)
    phone_number: Optional[str] = Field(default=None, nullable=True)
    role: Optional[str] = Field(default="customer", nullable=False)
    is_active: bool = Field(default=True, nullable=False)

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
