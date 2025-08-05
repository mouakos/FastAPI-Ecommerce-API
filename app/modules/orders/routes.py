from fastapi import APIRouter, Depends, status
from typing import Annotated, List
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession

from ...database.core import get_session
from ..auth.dependencies import AccessToken, RoleChecker
from .schemas import OrderCreate, OrderRead, OrderStatusUpdate
from .service import OrderService

router = APIRouter(prefix="/api/v1", tags=["orders"])

role_checker_admin = Depends(RoleChecker(["admin"]))

DbSession = Annotated[AsyncSession, Depends(get_session)]


@router.post(
    "/users/me/orders",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_order(
    db: DbSession,
    token_data: AccessToken,
    data: OrderCreate,
):
    return await OrderService.create_order(db, token_data.get_uuid(), data)


@router.get("/users/me/orders", response_model=List[OrderRead])
async def list_my_orders(
    db: DbSession,
    token_data: AccessToken,
):
    return await OrderService.list_orders_by_user(db, token_data.get_uuid())


@router.get("/users/me/orders/{order_id}", response_model=OrderRead)
async def get_my_order(
    order_id: UUID,
    db: DbSession,
    token_data: AccessToken,
):
    return await OrderService.get_order_by_user(db, token_data.get_uuid(), order_id)


@router.get(
    "/users/{user_id}/orders/{order_id}",
    response_model=OrderRead,
    dependencies=[role_checker_admin],
)
async def get_order(
    order_id: UUID,
    user_id: UUID,
    db: DbSession,
):
    return await OrderService.get_order_by_user(db, user_id, order_id)


@router.get(
    "/users/{user_id}/orders",
    response_model=List[OrderRead],
    dependencies=[role_checker_admin],
)
async def list_orders_by_user(
    user_id: UUID,
    db: DbSession,
):
    return await OrderService.list_orders_by_user(db, user_id)


@router.patch(
    "/users/{user_id}/orders/{order_id}/status",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[role_checker_admin],
)
async def update_order_status(
    user_id: UUID,
    order_id: UUID,
    order_status: OrderStatusUpdate,
    db: DbSession,
):
    await OrderService.update_order_status(db, user_id, order_id, order_status.status)
