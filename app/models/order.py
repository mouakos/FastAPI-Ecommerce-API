from typing import Optional, TYPE_CHECKING
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

    id: int | None = Field(default=None, primary_key=True)
    shipping_address_id: int = Field(foreign_key="addresses.id", nullable=False)
    billing_address_id: int | None = Field(foreign_key="addresses.id", nullable=False)
    user_id: int = Field(foreign_key="users.id", nullable=False)
    status: OrderStatus = Field(default=OrderStatus.PENDING, nullable=False)
    total_amount: float = Field(default=0.0, nullable=False)

    # Relationship with user - many-to-one
    user: Optional["User"] = Relationship(back_populates="orders")

    # Relationship with order items - one-to-many
    items: list["OrderItem"] = Relationship(
        back_populates="order", sa_relationship_kwargs={"lazy": "selectin"}
    )


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"

    id: int | None = Field(default=None, primary_key=True)

    product_id: int = Field(foreign_key="products.id", nullable=False)
    order_id: int = Field(foreign_key="orders.id", nullable=False)
    quantity: int = Field(default=1, nullable=False)
    unit_price: float = Field(nullable=False)
    subtotal: float = Field(nullable=False)

    # Relationship with order - many-to-one
    order: Optional[Order] = Relationship(back_populates="items")
