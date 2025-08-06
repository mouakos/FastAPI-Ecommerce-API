from fastapi import APIRouter, Depends, status
from typing import Annotated
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database.core import get_session
from app.modules.auth.dependencies import AccessToken, RoleChecker
from .schemas import CartItemCreate, CartItemRead, CartItemUpdate, CartRead
from .service import CartService


router = APIRouter(prefix="/api/v1/users", tags=["Cart"])
role_checker_admin = Depends(RoleChecker(["admin"]))

DbSession = Annotated[AsyncSession, Depends(get_session)]


@router.get("/me/cart", response_model=list[CartRead])
async def get_my_cart(
    db: DbSession,
    token_data: AccessToken,
):
    return await CartService.get_cart(db, token_data.get_int())


@router.post(
    "/me/cart/items",
    response_model=CartItemRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_item_to_my_cart(
    data: CartItemCreate,
    db: DbSession,
    token_data: AccessToken,
):
    return await CartService.add_item(db, token_data.get_int(), data)


@router.patch("/me/cart/items/{item_id}", response_model=CartItemRead)
async def update_item_in_my_cart(
    item_id: int,
    data: CartItemUpdate,
    db: DbSession,
    token_data: AccessToken,
):
    return await CartService.update_item(db, token_data.get_int(), item_id, data)


@router.delete("/me/cart/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_item_from_my_cart(
    item_id: int,
    db: DbSession,
    token_data: AccessToken,
):
    await CartService.remove_item(db, token_data.get_int(), item_id)


@router.delete("/me/cart/clear", status_code=status.HTTP_204_NO_CONTENT)
async def clear_my_cart(
    db: DbSession,
    token_data: AccessToken,
):
    await CartService.clear_cart(db, token_data.get_int())


@router.get(
    "/{user_id}/cart",
    response_model=list[CartRead],
    dependencies=[role_checker_admin],
)
async def get_cart(
    user_id: int,
    db: DbSession,
):
    return await CartService.get_cart(db, user_id)
