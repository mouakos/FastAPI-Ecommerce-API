from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .cart import Cart
    from .product import Product


class CartItem(SQLModel, table=True):
    __tablename__ = "cart_items"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    quantity: int = Field(default=1, nullable=False)
    unit_price: float = Field(nullable=False)
    subtotal: float = Field(nullable=False)

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships with cart - many-to-one
    cart_id: UUID = Field(foreign_key="carts.id", nullable=False)
    cart: "Cart" = Relationship(back_populates="items")

    # Relationship with product - many-to-one
    product_id: UUID = Field(foreign_key="products.id", nullable=False)
    product: "Product" = Relationship(back_populates="cart_items")
