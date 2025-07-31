from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID


class CartItemBase(BaseModel):
    product_id: UUID = Field(..., description="Unique identifier for the product")
    quantity: int = Field(..., ge=1, description="Quantity must be at least 1")


class CartItemCreate(CartItemBase):
    pass


class CartItemRead(CartItemBase):
    id: UUID = Field(..., description="Unique identifier for the cart item")
    unit_price: float = Field(..., description="Unit price of the product")
    subtotal: float = Field(..., description="Subtotal price of the item in the cart")


class CartItemUpdate(CartItemBase):
    quantity: Optional[int] = Field(
        ..., ge=1, description="Quantity must be at least 1"
    )


class CartRead(BaseModel):
    id: UUID = Field(..., description="Unique identifier for the cart")
    user_id: UUID = Field(
        ..., description="Unique identifier for the user who owns the cart"
    )
    items: list[CartItemRead] = Field(..., description="List of items in the cart")
    total_amount: float = Field(..., description="Total amount of the cart")
