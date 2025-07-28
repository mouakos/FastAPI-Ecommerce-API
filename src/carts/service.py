from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from fastapi import HTTPException
from datetime import datetime


from src.carts.schemas import CartItemCreate, CartItemUpdate
from src.models.cart import Cart
from src.models.cart_item import CartItem


class CartService:
    @staticmethod
    async def get_or_create_cart(db: AsyncSession, user_id: UUID) -> Cart:
        """Get or create a cart for the user.

        Args:
            db (AsyncSession): Database session.
            user_id (UUID): Unique identifier for the user.

        Returns:
            Cart: The user's cart.
        """
        stmt = select(Cart).where(Cart.user_id == user_id)
        result = await db.exec(stmt)
        cart = result.first()
        if cart:
            return cart

        cart = Cart(user_id=user_id)
        db.add(cart)
        await db.commit()
        await db.refresh(cart)
        return cart

    @staticmethod
    async def get_cart_items(db: AsyncSession, user_id: UUID) -> list[CartItem]:
        cart = await CartService.get_or_create_cart(db, user_id)
        stmt = select(CartItem).where(CartItem.cart_id == cart.id)
        result = await db.exec(stmt)
        return result.all()

    @staticmethod
    async def add_item(
        db: AsyncSession, user_id: UUID, data: CartItemCreate
    ) -> CartItem:
        """Add an item to the user's cart.

        Args:
            db (AsyncSession): Database session.
            user_id (UUID): Unique identifier for the user.
            data (CartItemCreate): Cart item data to add.

        Returns:
            CartItem: The created cart item.
        """
        cart = await CartService.get_or_create_cart(db, user_id)

        stmt = select(CartItem).where(
            CartItem.cart_id == cart.id, CartItem.product_id == data.product_id
        )
        result = await db.exec(stmt)
        item = result.first()

        if item:
            item.quantity += data.quantity
        else:
            item = CartItem(
                cart_id=cart.id, product_id=data.product_id, quantity=data.quantity
            )

        db.add(item)
        await db.commit()
        await db.refresh(item)
        return item

    @staticmethod
    async def update_item(
        db: AsyncSession, user_id: UUID, item_id: UUID, data: CartItemUpdate
    ) -> CartItem:
        """Update the quantity of an item in the user's cart.

        Args:
            db (AsyncSession): Database session.
            user_id (UUID): Unique identifier for the user.
            item_id (UUID): Unique identifier for the cart item.
            data (CartItemUpdate): Updated cart item data.

        Raises:
            HTTPException: If the cart item is not found.

        Returns:
            CartItem: The updated cart item.
        """
        cart = await CartService.get_or_create_cart(db, user_id)

        stmt = select(CartItem).where(
            CartItem.id == item_id, CartItem.cart_id == cart.id
        )
        result = await db.exec(stmt)
        item = result.first()

        if not item:
            raise HTTPException(status_code=404, detail="Cart item not found.")

        item.quantity = data.quantity
        item.updated_at = datetime.utcnow()

        db.add(item)
        await db.commit()
        await db.refresh(item)
        return item

    @staticmethod
    async def remove_item(db: AsyncSession, user_id: UUID, item_id: UUID) -> None:
        """Remove an item from the user's cart.

        Args:
            db (AsyncSession): Database session.
            user_id (UUID): Unique identifier for the user.
            item_id (UUID): Unique identifier for the cart item.

        Raises:
            HTTPException: If the cart item is not found.
        """
        cart = await CartService.get_or_create_cart(db, user_id)
        stmt = select(CartItem).where(
            CartItem.id == item_id, CartItem.cart_id == cart.id
        )
        result = await db.exec(stmt)
        item = result.first()

        if not item:
            raise HTTPException(status_code=404, detail="Item not found.")

        await db.delete(item)
        await db.commit()

    @staticmethod
    async def clear_cart(db: AsyncSession, user_id: UUID) -> None:
        """Clear the user's cart.

        Args:
            db (AsyncSession): Database session.
            user_id (UUID): Unique identifier for the user.
        """
        cart = await CartService.get_or_create_cart(db, user_id)
        for item in cart.items:
            await db.delete(item)

        await db.commit()
