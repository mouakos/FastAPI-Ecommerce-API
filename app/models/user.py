from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime, date
from uuid import UUID, uuid4

from app.models.cart import Cart

if TYPE_CHECKING:
    from app.models.review import Review


class Gender(str, Enum):
    male = "male"
    female = "female"
    other = "other"


class UserRole(str, Enum):
    customer = "customer"
    admin = "admin"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(index=True, nullable=False, unique=True)
    password_hash: str = Field(nullable=False, exclude=True)
    full_name: str = Field(nullable=False)
    gender: Gender = Field(nullable=False)
    date_of_birth: Optional[date] = Field(default=None, nullable=True)
    phone_number: Optional[str] = Field(default=None, nullable=True)
    role: UserRole = Field(default=UserRole.customer, nullable=False)
    is_active: bool = Field(default=True, nullable=False)

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship with reviews - one-to-many
    reviews: list["Review"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )

    # Relationship with cart - one-to-one
    cart: "Cart" = Relationship(back_populates="user")
