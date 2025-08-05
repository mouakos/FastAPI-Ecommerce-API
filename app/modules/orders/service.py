from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.exceptions import ConflictError, NotFoundError
from app.modules.addresses.service import AddressService
from app.modules.users.service import UserService
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.modules.carts.service import CartService
from .schemas import OrderCreate, OrderRead, OrderStatus


class OrderService:
    @staticmethod
    async def create_order(
        db: AsyncSession, user_id: UUID, data: OrderCreate
    ) -> OrderRead:
        """Create a new order for a user.

        Args:
            db (AsyncSession): The database session.
            user_id (UUID): The ID of the user to create the order for.
            data (OrderCreate): The data for the new order.

        Raises:
            ConflictError: If the cart is empty or if any product is out of stock.
            NotFoundError: If the shipping or billing address or user is not found.

        Returns:
            OrderRead: The created order.
        """
        cart = await CartService.get_cart(db, user_id)

        shipping_address = await AddressService.get_user_address(
            db, user_id, data.shipping_address_id
        )

        if data.billing_address_id:
            billing_address = await AddressService.get_user_address(
                db, user_id, data.billing_address_id
            )
        else:
            billing_address = shipping_address

        # validate inventory & snapshot unit prices
        order_items: list[OrderItem] = []
        for item in cart.items:
            product = await db.get(Product, item.product_id)
            if not product or product.stock < item.quantity:
                raise ConflictError(
                    f"Product {item.product_id} is out of stock or insufficient quantity.",
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
            shipping_address_id=shipping_address.id,
            billing_address_id=billing_address.id,
        )
        db.add(order)
        await db.commit()
        return order

    @staticmethod
    async def get_order_by_user(
        db: AsyncSession, user_id: UUID, order_id: UUID
    ) -> OrderRead:
        """Get an order by its ID for a specific user.

        Args:
            db (AsyncSession): The database session.
            order_id (UUID): The ID of the order to retrieve.
            user_id (UUID): The ID of the user who owns the order.

        Raises:
            NotFoundError: If the user or order is not found.

        Returns:
            OrderRead: The retrieved order.
        """
        result = await db.exec(
            select(Order).where(Order.id == order_id, Order.user_id == user_id)
        )
        order = result.first()
        if not order:
            raise NotFoundError(
                f"Order with ID {order_id} not found for user {user_id}"
            )
        return order

    @staticmethod
    async def list_orders_by_user(db: AsyncSession, user_id: UUID) -> list[OrderRead]:
        """List all orders for a specific user.

        Args:
            db (AsyncSession): The database session.
            user_id (UUID): The ID of the user to list orders for.

        Returns:
            list[OrderRead]: The list of orders for the user.
        """
        user = await UserService.get_user(db, user_id)

        stmt = select(Order).where(Order.user_id == user.id)
        result = await db.exec(stmt)
        return result.all()

    @staticmethod
    async def update_order_status(
        db: AsyncSession, user_id: UUID, order_id: UUID, order_status: OrderStatus
    ) -> OrderRead:
        """Update the status of an order.

        Args:
            db (AsyncSession): The database session.
            user_id (UUID): The ID of the user who owns the order.
            order_id (UUID): The ID of the order to update.
            order_status (OrderStatus): The new status for the order.

        Raises:
            NotFoundError: If the user or order is not found.
        Returns:
            OrderRead: The updated order.
        """
        user = await UserService.get_user(db, user_id)

        result = await db.exec(
            select(Order).where(Order.id == order_id, Order.user_id == user.id)
        )
        order = result.first()
        if not order:
            raise NotFoundError(
                f"Order with ID {order_id} not found for user {user_id}"
            )

        order.status = order_status.value
        await db.commit()
        return order
