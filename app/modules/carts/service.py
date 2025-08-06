from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.exceptions import ConflictError, NotFoundError
from app.models.cart import Cart, CartItem
from app.modules.products.service import ProductService
from app.modules.users.service import UserService
from .schemas import CartItemCreate, CartItemUpdate, CartRead


class CartService:
    @staticmethod
    async def get_cart(db: AsyncSession, user_id: int) -> CartRead:
        """Get the cart for a specific user.

        Args:
            db (AsyncSession): Database session.
            user_id (int): Unique identifier for the user.
        Raises:
            NotFoundError: If the user does not exist.

        Returns:
            Cart: The user's cart.
        """
        cart = await CartService._get_or_create_cart(db, user_id)
        return cart

    @staticmethod
    async def add_item(
        db: AsyncSession, user_id: int, data: CartItemCreate
    ) -> CartItem:
        """Add an item to the user's cart.

        Args:
            db (AsyncSession): Database session.
            user_id (int): Unique identifier for the user.
            data (CartItemCreate): Cart item data to add.
        Raises:
            NotFoundError: If the product or user does not exist.
            ConflictError: If the requested quantity exceeds available stock.

        Returns:
            CartItem: The created cart item.
        """
        cart = await CartService._get_or_create_cart(db, user_id)
        product = await ProductService.get_product(db, data.product_id)

        if data.quantity > product.stock:
            raise ConflictError("Requested quantity exceeds available stock")

        stmt = select(CartItem).where(
            CartItem.cart_id == cart.id, CartItem.product_id == data.product_id
        )
        result = await db.exec(stmt)
        item = result.first()

        if item:
            item.quantity += data.quantity
            item.subtotal = item.unit_price * item.quantity
        else:
            item = CartItem(
                cart_id=cart.id,
                product_id=data.product_id,
                quantity=data.quantity,
                unit_price=product.price,
                subtotal=product.price * data.quantity,
            )

        cart.total_amount += item.subtotal

        db.add(item)
        await db.commit()
        return item

    @staticmethod
    async def update_item(
        db: AsyncSession, user_id: int, item_id: int, data: CartItemUpdate
    ) -> CartItem:
        """Update the quantity of an item in the user's cart.

        Args:
            db (AsyncSession): Database session.
            user_id (int): Unique identifier for the user.
            item_id (int): Unique identifier for the cart item.
            data (CartItemUpdate): Updated cart item data.

        Raises:
            NotFoundError: If the user or item does not exist.
            ConflictError: If the requested quantity exceeds available stock.

        Returns:
            CartItem: The updated cart item.
        """
        cart = await CartService._get_or_create_cart(db, user_id)

        stmt = select(CartItem).where(
            CartItem.id == item_id, CartItem.cart_id == cart.id
        )
        result = await db.exec(stmt)
        item = result.first()

        if not item:
            raise NotFoundError(f"Cart item with ID {item_id} not found")

        if data.quantity > item.product.stock:
            raise ConflictError("Requested quantity exceeds available stock")

        old_subtotal = item.subtotal
        item.quantity = data.quantity
        item.subtotal = item.unit_price * item.quantity
        cart.total_amount += item.subtotal - old_subtotal

        db.add(item)
        await db.commit()
        return item

    @staticmethod
    async def remove_item(db: AsyncSession, user_id: int, item_id: int) -> None:
        """Remove an item from the user's cart.

        Args:
            db (AsyncSession): Database session.
            user_id (int): Unique identifier for the user.
            item_id (int): Unique identifier for the cart item.

        Raises:
            NotFoundError: If the user or cart item does not exist.
        """
        cart = await CartService._get_or_create_cart(db, user_id)

        if not cart.items:
            return

        stmt = select(CartItem).where(
            CartItem.id == item_id, CartItem.cart_id == cart.id
        )
        result = await db.exec(stmt)
        item = result.first()

        if not item:
            raise NotFoundError(f"Item with ID {item_id} not found")

        cart.total_amount -= item.subtotal

        await db.delete(item)
        await db.commit()

    @staticmethod
    async def clear_cart(db: AsyncSession, user_id: int) -> None:
        """Clear the user's cart.

        Args:
            db (AsyncSession): Database session.
            user_id (int): Unique identifier for the user.

        Raises:
            NotFoundError: If the user does not exist.
        """
        cart = await CartService._get_or_create_cart(db, user_id)

        for item in cart.items:
            await db.delete(item)

        cart.total_amount = 0

        await db.commit()

    @staticmethod
    async def _get_or_create_cart(db: AsyncSession, user_id: int) -> Cart:
        """Get or create a cart for the user.

        Args:
            db (AsyncSession): Database session.
            user_id (int): Unique identifier for the user.
        Raises:
            NotFoundError: If the user does not exist.
        Returns:
            Cart: The user's cart.
        """
        user = await UserService.get_user(db, user_id)

        stmt = select(Cart).where(Cart.user_id == user.id)
        result = await db.exec(stmt)
        cart = result.first()
        if cart:
            return cart

        cart = Cart(user_id=user_id)
        db.add(cart)
        await db.commit()
        return cart
