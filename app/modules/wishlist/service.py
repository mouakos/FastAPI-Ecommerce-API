from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.models.wishlist import Wishlist, WishlistItem
from app.modules.products.service import ProductService
from app.modules.users.service import UserService
from .schemas import WishlistRead, WishlistItemCreate, WishlistItemRead


class WishlistService:
    @staticmethod
    async def get_user_wishlist(db: AsyncSession, user_id: int) -> WishlistRead:
        """
        Get the user's wishlist with items.
        Args:
            db (AsyncSession): The database session.
            user_id (int): The user's unique identifier.
        Raise:
            ResourceNotFound: If the user does not exist.
        Returns:
            WishlistRead: The user's wishlist with items.
        """
        return await WishlistService._get_or_create_user_wishlist(db, user_id)

    @staticmethod
    async def add_item_to_user_wishlist(
        db: AsyncSession, user_id: int, data: WishlistItemCreate
    ) -> WishlistItemRead:
        """
        Add an item to the user's wishlist.
        Args:
            db (AsyncSession): The database session.
            user_id (int): The user's unique identifier.
            data (WishlistItemCreate): The wishlist item to add.
        Raise:
            ResourceNotFound: If the user or product does not exist.
        Returns:
            WishlistItemRead: The created or existing wishlist item.
        """

        wishlist = await WishlistService._get_or_create_user_wishlist(db, user_id)

        product = await ProductService.get_product(db, data.product_id)

        for item in wishlist.items:
            if item.product_id == product.id:
                return item

        item = WishlistItem(
            wishlist_id=wishlist.id,
            product_id=data.product_id,
        )
        item = await db.add(item)
        await db.commit()
        return item

    @staticmethod
    async def remove_item_from_user_wishlist(
        db: AsyncSession, user_id: int, product_id: int
    ) -> None:
        """
        Remove an item from the user's wishlist.
        Args:
            db (AsyncSession): The database session.
            user_id (int): The user's unique identifier.
            product_id (int): The product's unique identifier to remove from wishlist.
        Raise:
            ResourceNotFound: If the user or product does not exist.
        """
        wishlist = await WishlistService._get_or_create_user_wishlist(db, user_id)

        product = await ProductService.get_product(db, product_id)
        for item in wishlist.items:
            if item.product_id == product.id:
                await db.delete(item)
                await db.commit()
                return

    @staticmethod
    async def clear_user_wishlist(db: AsyncSession, user_id: int) -> None:
        """
        Remove all items from the user's wishlist.
        Args:
            db (AsyncSession): The database session.
            user_id (int): The user's unique identifier.
        Raise:
            ResourceNotFound: If the user does not exist.
        """
        wishlist = await WishlistService._get_or_create_user_wishlist(db, user_id)
        for item in wishlist.items:
            await db.delete(item)
        await db.commit()

    @staticmethod
    async def _get_or_create_user_wishlist(db: AsyncSession, user_id: int) -> Wishlist:
        """
        Get or create a wishlist for the user.
        Args:
            db (AsyncSession): The database session.
            user_id (int): The user's unique identifier.
        Raise:
            ResourceNotFound: If the user does not exist.
        Returns:
            Wishlist: The user's wishlist.
        """
        user = await UserService.get_user(db, user_id)

        result = await db.exec(select(Wishlist).where(Wishlist.user_id == user.id))
        wishlist = result.first()

        if not wishlist:
            wishlist = Wishlist(user_id=user.id)
            await db.add(wishlist)
            await db.commit()
        return wishlist
