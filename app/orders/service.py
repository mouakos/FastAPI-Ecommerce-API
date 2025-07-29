from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from fastapi import HTTPException, status

from app.carts.service import CartService
from app.models.address import Address
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.orders.schemas import OrderCreate, OrderStatus


class OrderService:
    @staticmethod
    async def create_order(db: AsyncSession, user_id: UUID, data: OrderCreate) -> Order:
        cart = await CartService.get_cart(db, user_id)

        if not cart.items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cart is empty, cannot create order.",
            )

        shipping_address = db.get(Address, data.shipping_address_id)
        if not shipping_address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shipping address not found.",
            )

        if data.billing_address_id:
            billing_address = db.get(Address, data.billing_address_id)
            if data.billing_address_id and not billing_address:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Billing address not found.",
                )

        # validate inventory & snapshot unit prices
        order_items: list[OrderItem] = []
        for item in cart.items:
            product = await db.get(Product, item.product_id)
            if not product or product.stock < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product {item.product_id} is out of stock or insufficient quantity.",
                )
            product.stock -= item.quantity
            order_items.append(
                OrderItem(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    subtotal=item.subtotal,
                )
            )

        # Create order
        order = Order(
            user_id=user_id,
            items=order_items,
            total_amount=cart.total_amount,
            shipping_address_id=data.shipping_address_id,
            billing_address_id=data.billing_address_id,
        )
        db.add(order)
        await db.commit()
        await db.refresh(order)
        return order

    @staticmethod
    async def get_order_by_id(db: AsyncSession, order_id: UUID) -> Optional[Order]:
        result = await db.execute(select(Order).where(Order.id == order_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_order_by_user(db: AsyncSession, user_id: UUID) -> Optional[Order]:
        result = await db.exec(select(Order).where(Order.user_id == user_id))
        return result.first()

    @staticmethod
    async def list_orders_by_user(db: AsyncSession, user_id: UUID) -> list[Order]:
        result = await db.exec(
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
        )
        return result.all()

    @staticmethod
    async def update_order_status(
        db: AsyncSession, order_id: UUID, order_status: OrderStatus
    ) -> Order:
        result = await db.exec(select(Order).where(Order.id == order_id))
        order = result.first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
            )

        if order.status.value != order_status.value:
            # Only update if the status is changing
            order.status = order_status
            order.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(order)
        return order
