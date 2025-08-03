from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum


if TYPE_CHECKING:
    from .user import User


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order(SQLModel, table=True):
    __tablename__ = "orders"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    status: OrderStatus = Field(default=OrderStatus.PENDING, nullable=False)
    total_amount: float = Field(default=0.0, nullable=False)

    # Relationship with user - many-to-one
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    user: Optional["User"] = Relationship(back_populates="orders")

    # Relationship with order items - one-to-many
    items: list["OrderItem"] = Relationship(
        back_populates="order", sa_relationship_kwargs={"lazy": "selectin"}
    )

    # Relationship with addresses
    shipping_address_id: UUID = Field(
        foreign_key="addresses.id", nullable=False, index=True
    )
    billing_address_id: Optional[UUID] = Field(
        default=None, foreign_key="addresses.id", index=True
    )


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    product_id: UUID = Field(foreign_key="products.id", nullable=False, index=True)
    quantity: int = Field(default=1, nullable=False)
    unit_price: float = Field(nullable=False)
    subtotal: float = Field(nullable=False)

    # Relationship with order - many-to-one
    order_id: UUID = Field(foreign_key="orders.id", nullable=False, index=True)
    order: Optional[Order] = Relationship(back_populates="items")
