# routes/cart.py

from fastapi import APIRouter
from uuid import UUID

from src.carts.schemas import CartItemCreate, CartItemUpdate, CartRead
from src.carts.service import CartService
from src.core.dependencies import DbSession, CurrentUser
from src.models.cart_item import CartItem

router = APIRouter(prefix="/api/v1/cart", tags=["Carts"])


@router.get("", response_model=CartRead)
async def get_cart(
    db: DbSession,
    current_user: CurrentUser,
):
    cart = await CartService.get_or_create_cart(db, current_user.id)
    return cart


@router.post("/{product_id}", response_model=CartRead)
async def add_to_cart(
    product_id: UUID,
    cart_item_create: CartItemCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    cart = await CartService.add_item(db, current_user.id, product_id, cart_item_create)
    return cart


@router.put("/{product_id}", response_model=CartItem)
async def update_cart_item(
    product_id: UUID,
    cart_item_update: CartItemUpdate,
    db: DbSession,
    current_user: CurrentUser,
):
    cart = await CartService.update_item(
        db, current_user.id, product_id, cart_item_update
    )
    return cart


@router.delete("/{product_id}", response_model=CartItem)
async def remove_from_cart(
    product_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
):
    cart = await CartService.remove_item(db, current_user.id, product_id)
    return cart
