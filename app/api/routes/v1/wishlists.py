from fastapi import APIRouter, status
from uuid import UUID
from app.api.dependencies import DbSession, CurrentUser
from app.wishlist.service import WishlistService
from app.wishlist.schemas import WishlistRead, WishlistItemCreate, WishlistItemRead

router = APIRouter(prefix="/wishlists", tags=["Wishlists"])


@router.get("/", response_model=WishlistRead, summary="Get current user's wishlist")
async def get_my_wishlist(db: DbSession, current_user: CurrentUser) -> WishlistRead:
    return await WishlistService.get_wishlist(db, current_user.id)


@router.post(
    "/items",
    response_model=WishlistItemRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add item to wishlist",
)
async def add_item(
    data: WishlistItemCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> WishlistItemRead:
    return await WishlistService.add_item(db, current_user.id, data)


@router.delete(
    "/items/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove item from wishlist",
)
async def remove_item(
    product_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
):
    await WishlistService.remove_item(db, current_user.id, product_id)


@router.delete(
    "/clear", status_code=status.HTTP_204_NO_CONTENT, summary="Clear wishlist"
)
async def clear_wishlist(db: DbSession, current_user: CurrentUser):
    await WishlistService.clear_wishlist(db, current_user.id)
