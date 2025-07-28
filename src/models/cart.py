from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User
    from .cart_item import CartItem


class Cart(SQLModel, table=True):
    __tablename__ = "carts"
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    total_amount: float = Field(default=0.0, nullable=False)

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship with user - one-to-one
    user_id: UUID = Field(foreign_key="users.id", nullable=False, unique=True)
    user: "User" = Relationship(back_populates="cart")

    # Relationship with cart items - one-to-many
    items: list["CartItem"] = Relationship(back_populates="cart")
