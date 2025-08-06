from typing import TYPE_CHECKING, Optional
from sqlmodel import SQLModel, Field, Relationship


if TYPE_CHECKING:
    from .user import User
    from .product import Product


class Cart(SQLModel, table=True):
    __tablename__ = "carts"
    id: int | None = Field(default=None, primary_key=True)

    total_amount: float = Field(default=0.0, nullable=False)

    # Relationship with user - one-to-one
    user_id: int = Field(foreign_key="users.id", nullable=False, unique=True)
    user: "User" = Relationship(back_populates="cart")

    # Relationship with cart items - one-to-many
    items: list["CartItem"] = Relationship(back_populates="cart")


class CartItem(SQLModel, table=True):
    __tablename__ = "cart_items"

    id: int | None = Field(default=None, primary_key=True)

    quantity: int = Field(nullable=False)
    unit_price: float = Field(nullable=False)
    subtotal: float = Field(nullable=False)

    # Relationships with cart - many-to-one
    cart_id: int = Field(foreign_key="carts.id", nullable=False)
    cart: "Cart" = Relationship(back_populates="items")

    # Relationship with product - many-to-one
    product_id: int = Field(foreign_key="products.id", nullable=False)
    product: Optional["Product"] = Relationship(back_populates="cart_items")
