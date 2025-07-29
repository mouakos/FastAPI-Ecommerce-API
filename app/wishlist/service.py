from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from datetime import datetime

from app.models.whishlist import Wishlist, WishlistItem
from app.wishlist.schemas import (
    WishlistRead,
    WishlistItemCreate,
    WishlistItemRead,
)
from app.models.product import Product
from app.core.exceptions import ProductNotFound


class WishlistService:
    @staticmethod
    async def get_or_create_wishlist(db: AsyncSession, user_id: UUID) -> Wishlist:
        """Get or create a wishlist for the user.

        Args:
            db (AsyncSession): Database session.
            user_id (UUID): Unique identifier for the user.

        Returns:
            Wishlist: The user's wishlist.
        """
        stmt = select(Wishlist).where(Wishlist.user_id == user_id)
        result = await db.exec(stmt)
        wishlist = result.first()
        if wishlist:
            return wishlist
        wishlist = Wishlist(user_id=user_id)
        db.add(wishlist)
        await db.commit()
        await db.refresh(wishlist)
        return wishlist

    @staticmethod
    async def get_wishlist(db: AsyncSession, user_id: UUID) -> WishlistRead:
        """Get the user's wishlist with items.

        Args:
            db (AsyncSession): Database session.
            user_id (UUID): Unique identifier for the user.

        Returns:
            WishlistRead: The user's wishlist.
        """
        wishlist = await WishlistService.get_or_create_wishlist(db, user_id)
        # Eager load items
        stmt = select(WishlistItem).where(WishlistItem.wishlist_id == wishlist.id)
        items = (await db.exec(stmt)).all()
        return WishlistRead(
            id=wishlist.id,
            user_id=wishlist.user_id,
            created_at=wishlist.created_at,
            items=[WishlistItemRead(**item.model_dump()) for item in items],
        )

    @staticmethod
    async def add_item(
        db: AsyncSession, user_id: UUID, data: WishlistItemCreate
    ) -> WishlistItemRead:
        """Add an item to the user's wishlist.

        Args:
            db (AsyncSession): Database session.
            user_id (UUID): Unique identifier for the user.
            data (WishlistItemCreate): Wishlist item data to add.

        Raises:
            ProductNotFound: If the product does not exist.

        Returns:
            WishlistItemRead: The created wishlist item.
        """

        wishlist = await WishlistService.get_or_create_wishlist(db, user_id)
        # Check if product exists
        product = await db.get(Product, data.product_id)
        if not product:
            raise ProductNotFound()
        # Check if already in wishlist
        stmt = select(WishlistItem).where(
            WishlistItem.wishlist_id == wishlist.id,
            WishlistItem.product_id == data.product_id,
        )
        result = await db.exec(stmt)
        item = result.first()
        if item:
            return WishlistItemRead(**item.model_dump())
        item = WishlistItem(
            wishlist_id=wishlist.id,
            product_id=data.product_id,
            added_at=datetime.utcnow(),
        )
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return WishlistItemRead(**item.model_dump())

    @staticmethod
    async def remove_item(db: AsyncSession, user_id: UUID, product_id: UUID) -> None:
        """Remove an item from the user's wishlist.

        Args:
            db (AsyncSession): Database session.
            user_id (UUID): Unique identifier for the user.
            product_id (UUID): Unique identifier for the product.
        """

        wishlist = await WishlistService.get_or_create_wishlist(db, user_id)
        stmt = select(WishlistItem).where(
            WishlistItem.wishlist_id == wishlist.id,
            WishlistItem.product_id == product_id,
        )
        result = await db.exec(stmt)
        item = result.first()
        if item:
            await db.delete(item)
            await db.commit()

    @staticmethod
    async def clear_wishlist(db: AsyncSession, user_id: UUID) -> None:
        """Clear all items in the user's wishlist.

        Args:
            db (AsyncSession): Database session.
            user_id (UUID): Unique identifier for the user.
        """
        wishlist = await WishlistService.get_or_create_wishlist(db, user_id)
        stmt = select(WishlistItem).where(WishlistItem.wishlist_id == wishlist.id)
        items = (await db.exec(stmt)).all()
        for item in items:
            await db.delete(item)
        await db.commit()
