from fastapi import APIRouter, status
from uuid import UUID
from typing import List

from app.carts.schemas import CartItemCreate, CartItemRead, CartItemUpdate, CartRead
from app.carts.service import CartService
from app.api.dependencies import DbSession, CurrentUser


router = APIRouter(prefix="/api/v1/cart", tags=["Carts"])


@router.get("/", response_model=List[CartRead], summary="Get the user's cart")
async def get_cart(
    db: DbSession,
    current_user: CurrentUser,
):
    return await CartService.get_or_create_cart(db, current_user.id)


@router.post("/items", response_model=CartItemRead, status_code=status.HTTP_201_CREATED)
async def add_item(
    data: CartItemCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    return await CartService.add_item(db, current_user.id, data)


@router.patch(
    "/items/{item_id}", response_model=CartItemRead, summary="Update cart item quantity"
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
    summary="Remove item from cart",
)
async def remove_item(
    item_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
):
    await CartService.remove_item(db, current_user.id, item_id)


@router.delete("/clear", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    db: DbSession,
    current_user: CurrentUser,
):
    await CartService.clear_cart(db, current_user.id)
