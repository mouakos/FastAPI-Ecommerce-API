from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession

from ...exceptions import NotFoundError
from ...models.product import Product
from ...models.user import User
from ...models.wishlist import Wishlist, WishlistItem
from .schemas import WishlistRead, WishlistItemCreate, WishlistItemRead


class WishlistService:
    @staticmethod
    async def get_wishlist(db: AsyncSession, user_id: UUID) -> WishlistRead:
        """
        Get the user's wishlist with items.
        Args:
            db (AsyncSession): The database session.
            user_id (UUID): The user's unique identifier.
        Raise:
            ResourceNotFound: If the user does not exist.
        Returns:
            WishlistRead: The user's wishlist with items.
        """
        user = await db.get(User, user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")

        wishlist = await db.get(Wishlist, user.id)
        if wishlist:
            return wishlist
        wishlist = Wishlist(user_id=user.id)
        await db.add(wishlist)
        await db.commit()
        return wishlist

    @staticmethod
    async def add_item(
        db: AsyncSession, user_id: UUID, data: WishlistItemCreate
    ) -> WishlistItemRead:
        """
        Add an item to the user's wishlist.
        Args:
            db (AsyncSession): The database session.
            user_id (UUID): The user's unique identifier.
            data (WishlistItemCreate): The wishlist item to add.
        Raise:
            ResourceNotFound: If the user or product does not exist.
        Returns:
            WishlistItemRead: The created or existing wishlist item.
        """
        user = await db.get(User, user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")

        product = await db.get(Product, data.product_id)
        if not product:
            raise NotFoundError(f"Product with ID {data.product_id} not found")

        wishlist = await db.get(Wishlist, user.id)

        if wishlist:
            for item in wishlist.items:
                if item.product_id == product.id:
                    return item
        else:
            wishlist = Wishlist(user_id=user.id)

        item = WishlistItem(
            wishlist_id=wishlist.id,
            product_id=data.product_id,
        )
        item = await db.add(item)
        await db.commit()
        return item

    @staticmethod
    async def remove_item(db: AsyncSession, user_id: UUID, product_id: UUID) -> None:
        """
        Remove an item from the user's wishlist.
        Args:
            db (AsyncSession): The database session.
            user_id (UUID): The user's unique identifier.
            product_id (UUID): The product's unique identifier to remove from wishlist.
        Raise:
            ResourceNotFound: If the user or product does not exist.
        """
        user = await db.get(User, user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")

        product = await db.get(Product, product_id)
        if not product:
            raise NotFoundError(f"Product with ID {product_id} not found")

        wishlist = await db.get(Wishlist, user.id)
        if wishlist is None:
            return
        for item in wishlist.items:
            if item.product_id == product.id:
                await db.delete(item)
                await db.commit()
                return

    @staticmethod
    async def clear_wishlist(db: AsyncSession, user_id: UUID) -> None:
        """
        Remove all items from the user's wishlist.
        Args:
            db (AsyncSession): The database session.
            user_id (UUID): The user's unique identifier.
        Raise:
            ResourceNotFound: If the user does not exist.
        """
        user = await db.get(User, user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")

        wishlist = await db.get(Wishlist, user.id)
        if wishlist is None:
            return
        for item in wishlist.items:
            await db.delete(item)
        await db.commit()
