from fastapi import APIRouter, Depends, status
from uuid import UUID
from typing import List

from app.carts.schemas import CartItemCreate, CartItemRead, CartItemUpdate, CartRead
from app.carts.service import CartService
from app.dependencies import DbSession, CurrentUser, RoleChecker
from app.users.schemas import UserRole

router = APIRouter(prefix="/api/v1/cart", tags=["Carts"])
role_checker_admin = Depends(RoleChecker([UserRole.admin]))


# User endpoints
@router.get("/", response_model=List[CartRead], summary="Get my cart")
async def get_my_cart(
    db: DbSession,
    current_user: CurrentUser,
):
    return await CartService.get_cart(db, current_user.id)


@router.post(
    "/items",
    response_model=CartItemRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add item to my cart",
)
async def add_item(
    data: CartItemCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    return await CartService.add_item(db, current_user.id, data)


@router.patch(
    "/items/{item_id}",
    response_model=CartItemRead,
    summary="Update cart item quantity",
)
async def update_item(
    item_id: UUID,
    data: CartItemUpdate,
    db: DbSession,
    current_user: CurrentUser,
):
    return await CartService.update_item(db, current_user.id, item_id, data)


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove item from my cart",
)
async def remove_item(
    item_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
):
    await CartService.remove_item(db, current_user.id, item_id)


@router.delete(
    "/clear",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Clear my cart",
)
async def clear_cart(
    db: DbSession,
    current_user: CurrentUser,
):
    await CartService.clear_cart(db, current_user.id)


# Admin endpoints
@router.get(
    "/admin/{user_id}",
    response_model=List[CartRead],
    dependencies=[role_checker_admin],
    summary="Get cart for a specific user (admin only)",
)
async def admin_get_cart_for_user(
    user_id: UUID,
    db: DbSession,
):
    return await CartService.get_cart(db, user_id)


@router.post(
    "/admin/{user_id}/items",
    response_model=CartItemRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[role_checker_admin],
    summary="Add item to user's cart (admin only)",
)
async def admin_add_item(
    user_id: UUID,
    data: CartItemCreate,
    db: DbSession,
):
    return await CartService.add_item(db, user_id, data)


@router.patch(
    "/admin/{user_id}/items/{item_id}",
    response_model=CartItemRead,
    dependencies=[role_checker_admin],
    summary="Update cart item quantity (admin only)",
)
async def admin_update_item(
    user_id: UUID,
    item_id: UUID,
    data: CartItemUpdate,
    db: DbSession,
):
    return await CartService.update_item(db, user_id, item_id, data)


@router.delete(
    "/admin/{user_id}/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[role_checker_admin],
    summary="Remove item from user's cart (admin only)",
)
async def admin_remove_item(
    user_id: UUID,
    item_id: UUID,
    db: DbSession,
):
    await CartService.remove_item(db, user_id, item_id)


@router.delete(
    "/admin/{user_id}/clear",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[role_checker_admin],
    summary="Clear user's cart (admin only)",
)
async def admin_clear_cart(
    user_id: UUID,
    db: DbSession,
):
    await CartService.clear_cart(db, user_id)
