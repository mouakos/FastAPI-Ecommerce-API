from fastapi import APIRouter, Depends, status
from uuid import UUID
from typing import Annotated

from sqlmodel.ext.asyncio.session import AsyncSession

from app.database.core import get_session
from app.modules.auth.dependencies import AccessToken, RoleChecker
from .schemas import CartItemCreate, CartItemRead, CartItemUpdate, CartRead
from .service import CartService


router = APIRouter(prefix="/api/v1/cart", tags=["Carts"])
role_checker_admin = Depends(RoleChecker(["admin"]))

DbSession = Annotated[AsyncSession, Depends(get_session)]


# User endpoints
@router.get("/me", response_model=list[CartRead])
async def get_my_cart(
    db: DbSession,
    token_data: AccessToken,
):
    return await CartService.get_cart(db, UUID(token_data.sub))


@router.post(
    "/items",
    response_model=CartItemRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_item_to_my_cart(
    data: CartItemCreate,
    db: DbSession,
    token_data: AccessToken,
):
    return await CartService.add_item(db, UUID(token_data.sub), data)


@router.patch(
    "/items/{item_id}",
    response_model=CartItemRead,
    summary="Update cart item quantity",
)
async def update_item_in_my_cart(
    item_id: UUID,
    data: CartItemUpdate,
    db: DbSession,
    token_data: AccessToken,
):
    return await CartService.update_item(db, UUID(token_data.sub), item_id, data)


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove item from my cart",
)
async def remove_item_from_my_cart(
    item_id: UUID,
    db: DbSession,
    token_data: AccessToken,
):
    await CartService.remove_item(db, UUID(token_data.sub), item_id)


@router.delete(
    "/clear",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Clear my cart",
)
async def clear_my_cart(
    db: DbSession,
    token_data: AccessToken,
):
    await CartService.clear_cart(db, UUID(token_data.sub))


# Admin endpoints
@router.get(
    "/users/{user_id}",
    response_model=list[CartRead],
    dependencies=[role_checker_admin],
)
async def get_cart(
    user_id: UUID,
    db: DbSession,
):
    return await CartService.get_cart(db, user_id)
