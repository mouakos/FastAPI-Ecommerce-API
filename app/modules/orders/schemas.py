from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class OrderItemCreate(BaseModel):
    product_id: UUID = Field(..., description="ID of the product in the order")
    quantity: int = Field(..., ge=1, description="Quantity of the product in the order")
    unit_price: float = Field(
        ..., description="Unit price of the product at the time of order"
    )


class OrderItemRead(OrderItemCreate):
    id: UUID = Field(..., description="Unique identifier of the order item")
    order_id: UUID = Field(..., description="ID of the order to which the item belongs")
    subtotal: float = Field(
        ..., description="Subtotal for the item (unit_price * quantity)"
    )
    created_at: datetime = Field(
        ..., description="Timestamp when the order item was created"
    )


class OrderCreate(BaseModel):
    shipping_address_id: UUID = Field(
        ..., description="ID of the shipping address for the order"
    )
    billing_address_id: Optional[UUID] = Field(
        default=None, description="ID of the billing address for the order"
    )


class OrderRead(BaseModel):
    id: UUID = Field(..., description="Unique identifier of the order")
    status: str = Field(..., description="Current status of the order")
    total_amount: float = Field(..., description="Total amount of the order")
    user_id: UUID = Field(..., description="ID of the user who placed the order")
    shipping_address_id: UUID = Field(
        ..., description="ID of the shipping address for the order"
    )
    billing_address_id: Optional[UUID] = Field(
        default=None, description="ID of the billing address for the order"
    )
    created_at: datetime = Field(
        ..., description="Timestamp when the order was created"
    )
    updated_at: datetime = Field(
        ..., description="Timestamp when the order was last updated"
    )
    items: list[OrderItemRead] = Field(
        default_factory=list, description="List of items in the order"
    )


class OrderStatus(str, Enum):
    PENDING: str = "pending"
    PAID: str = "paid"
    SHIPPED: str = "shipped"
    DELIVERED: str = "delivered"
    CANCELLED: str = "cancelled"


class OrderStatusUpdate(BaseModel):
    status: OrderStatus = Field(..., description="New status for the order")
