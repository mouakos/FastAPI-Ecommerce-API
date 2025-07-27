# services/cart.py

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from uuid import UUID
from src.models.cart import Cart
from src.models.cart_item import CartItem
from src.carts.schemas import CartItemCreate, CartItemUpdate
from src.core.exceptions import ProductNotFound


class CartService:
    @staticmethod
    async def get_or_create_cart(db: AsyncSession, user_id: UUID) -> Cart:
        result = await db.exec(select(Cart).where(Cart.user_id == user_id))
        cart = result.first()
        if not cart:
            cart = Cart(user_id=user_id)
            db.add(cart)
            await db.commit()
            await db.refresh(cart)
        return cart

    @staticmethod
    async def add_item(
        db: AsyncSession, user_id: UUID, product_id: UUID, item_data: CartItemCreate
    ) -> Cart:
        cart = await CartService.get_or_create_cart(db, user_id)

        result = await db.exec(
            select(CartItem).where(
                CartItem.cart_id == cart.id,
                CartItem.product_id == product_id,
            )
        )
        cart_item = result.first()
        if cart_item:
            cart_item.quantity += item_data.quantity
        else:
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=item_data.quantity,
            )
            db.add(cart_item)

        await db.commit()
        await db.refresh(cart)
        return cart

    @staticmethod
    async def remove_item(db: AsyncSession, user_id: UUID, product_id: UUID) -> Cart:
        cart = await CartService.get_or_create_cart(db, user_id)

        result = await db.exec(
            select(CartItem).where(
                CartItem.cart_id == cart.id,
                CartItem.product_id == product_id,
            )
        )
        cart_item = result.first()
        if not cart_item:
            raise ProductNotFound()

        await db.delete(cart_item)
        await db.commit()
        await db.refresh(cart)
        return cart

    @staticmethod
    async def update_item(
        db: AsyncSession, user_id: UUID, product_id: UUID, data: CartItemUpdate
    ) -> Cart:
        cart = await CartService.get_or_create_cart(db, user_id)

        result = await db.exec(
            select(CartItem).where(
                CartItem.cart_id == cart.id,
                CartItem.product_id == product_id,
            )
        )
        cart_item = result.first()
        if not cart_item:
            raise ProductNotFound()

        cart_item.quantity = data.quantity
        await db.commit()
        await db.refresh(cart)
        return cart
