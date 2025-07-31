from typing import Annotated
from fastapi import APIRouter, status, Depends
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.dependencies import AccessTokenBearer, RoleChecker
from app.auth.schemas import TokenData
from app.wishlist.service import WishlistService
from app.wishlist.schemas import WishlistRead, WishlistItemCreate, WishlistItemRead
from app.users.schemas import UserRole
from app.database.core import get_session

router = APIRouter(prefix="/api/v1/wishlists", tags=["Wishlists"])

role_checker_admin = Depends(RoleChecker([UserRole.admin]))
DbSession = Annotated[AsyncSession, Depends(get_session)]
AccessToken = Annotated[TokenData, Depends(AccessTokenBearer())]

# User endpoints
@router.get("/", response_model=WishlistRead, summary="Get current user's wishlist")
async def get_my_wishlist(db: DbSession, token_data: AccessToken) -> WishlistRead:
    return await WishlistService.get_wishlist(db, UUID(token_data.sub))


@router.post(
    "/items",
    response_model=WishlistItemRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add item to current user's wishlist",
)
async def add_item_to_my_wishlist(
    data: WishlistItemCreate,
    db: DbSession,
    token_data: AccessToken,
) -> WishlistItemRead:
    return await WishlistService.add_item(db, UUID(token_data.sub), data)


@router.delete(
    "/items/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove item from current user's wishlist",
)
async def remove_item_from_my_wishlist(
    product_id: UUID,
    db: DbSession,
    token_data: AccessToken,
):
    await WishlistService.remove_item(db, UUID(token_data.sub), product_id)


@router.delete(
    "/clear",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Clear current user's wishlist",
)
async def clear_my_wishlist(db: DbSession, token_data: AccessToken):
    await WishlistService.clear_wishlist(db, UUID(token_data.sub))


# Admin endpoints
@router.get(
    "/admin/{user_id}",
    response_model=WishlistRead,
    summary="Get wishlist for a user (admin)",
    dependencies=[role_checker_admin],
)
async def get_user_wishlist(user_id: UUID, db: DbSession):
    return await WishlistService.get_wishlist(db, user_id)


@router.post(
    "/admin/{user_id}/items",
    response_model=WishlistItemRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add item to user's wishlist (admin)",
    dependencies=[role_checker_admin],
)
async def add_item_to_user_wishlist(
    user_id: UUID, data: WishlistItemCreate, db: DbSession
) -> WishlistItemRead:
    return await WishlistService.add_item(db, user_id, data)


@router.delete(
    "/admin/{user_id}/items/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove item from user's wishlist (admin)",
    dependencies=[role_checker_admin],
)
async def remove_item_from_user_wishlist(
    user_id: UUID, product_id: UUID, db: DbSession
):
    await WishlistService.remove_item(db, user_id, product_id)


@router.delete(
    "/admin/{user_id}/clear",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Clear user's wishlist (admin)",
    dependencies=[role_checker_admin],
)
async def clear_user_wishlist(user_id: UUID, db: DbSession):
    await WishlistService.clear_wishlist(db, user_id)
