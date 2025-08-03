from typing import Annotated
from fastapi import APIRouter, status, Depends
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database.core import get_session
from app.modules.auth.dependencies import AccessToken, RoleChecker
from .service import WishlistService
from .schemas import WishlistRead, WishlistItemCreate, WishlistItemRead

router = APIRouter(prefix="/api/v1/wishlists", tags=["Wishlists"])

role_checker_admin = Depends(RoleChecker(["admin"]))
DbSession = Annotated[AsyncSession, Depends(get_session)]


# User endpoints
@router.get("/", response_model=WishlistRead)
async def get_my_wishlist(db: DbSession, token_data: AccessToken) -> WishlistRead:
    return await WishlistService.get_wishlist(db, UUID(token_data.sub))


@router.post(
    "/items", response_model=WishlistItemRead, status_code=status.HTTP_201_CREATED
)
async def add_item_to_my_wishlist(
    data: WishlistItemCreate,
    db: DbSession,
    token_data: AccessToken,
) -> WishlistItemRead:
    return await WishlistService.add_item(db, UUID(token_data.sub), data)


@router.delete("/items/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_item_from_my_wishlist(
    product_id: UUID,
    db: DbSession,
    token_data: AccessToken,
):
    await WishlistService.remove_item(db, UUID(token_data.sub), product_id)


@router.delete("/clear", status_code=status.HTTP_204_NO_CONTENT)
async def clear_my_wishlist(db: DbSession, token_data: AccessToken):
    await WishlistService.clear_wishlist(db, UUID(token_data.sub))


# Admin endpoints
@router.get(
    "/users/{user_id}",
    response_model=WishlistRead,
    dependencies=[role_checker_admin],
)
async def get_user_wishlist(user_id: UUID, db: DbSession):
    return await WishlistService.get_wishlist(db, user_id)
