from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from fastapi import HTTPException
from datetime import datetime

from app.carts.schemas import CartItemCreate, CartItemRead, CartItemUpdate, CartRead
from app.core.exceptions import CartItemNotFound, InsufficientStock, ProductNotFound, UserNotFound
from app.models.cart import Cart, CartItem
from app.models.product import Product


class CartService:
    @staticmethod
    async def get_cart(db: AsyncSession, user_id: UUID) -> CartRead:
        """Get the cart for a specific user.

        Args:
            db (AsyncSession): Database session.
            user_id (UUID): Unique identifier for the user.

        Returns:
            Cart: The user's cart.
        """
        cart = await CartService._get_or_create_cart(db, user_id)

        return CartRead(
            id=cart.id,
            user_id=cart.user_id,
            items=[CartItemRead(**cart_item.model_dump()) for cart_item in cart.items],
            total_amount=sum(item.subtotal for item in cart.items),
        )

    @staticmethod
    async def add_item(
        db: AsyncSession, user_id: UUID, data: CartItemCreate
    ) -> CartItem:
        """Add an item to the user's cart.

        Args:
            db (AsyncSession): Database session.
            user_id (UUID): Unique identifier for the user.
            data (CartItemCreate): Cart item data to add.
        Raises:
            ProductNotFound: If the product does not exist.

        Returns:
            CartItem: The created cart item.
        """
        cart = await CartService._get_or_create_cart(db, user_id)
        product = await db.get(Product, data.product_id)

        if not product:
            raise ProductNotFound()
        
        if data.quantity > product.stock:
            raise InsufficientStock()

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
            UserNotFound: If the user does not exist.

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
            raise CartItemNotFound()
        
        if data.quantity > item.product.stock:
            raise InsufficientStock()
            
        item.quantity = data.quantity
        item.subtotal = item.unit_price * item.quantity
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
            UserNotFound: If the user does not exist.
        """
        cart = await CartService._get_or_create_cart(db, user_id)
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
        cart = await CartService._get_or_create_cart(db, user_id)
        for item in cart.items:
            await db.delete(item)

        await db.commit()

    @staticmethod
    async def _get_or_create_cart(db: AsyncSession, user_id: UUID) -> Cart:
        """Get or create a cart for the user.

        Args:
            db (AsyncSession): Database session.
            user_id (UUID): Unique identifier for the user.
        Raises:
            UserNotFound: If the user does not exist.
        Returns:
            Cart: The user's cart.
        """
        user = await db.get(Cart, user_id)
        if not user:
            raise UserNotFound()
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
