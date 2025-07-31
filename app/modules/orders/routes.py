from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated, List
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.dependencies import AccessTokenBearer, RoleChecker
from app.auth.schemas import TokenData
from app.database.core import get_session
from app.orders.schemas import OrderRead, OrderStatusUpdate
from app.orders.service import OrderService
from app.users.schemas import UserRole

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])

role_checker_admin = Depends(RoleChecker([UserRole.admin]))

DbSession = Annotated[AsyncSession, Depends(get_session)]
AccessToken = Annotated[TokenData, Depends(AccessTokenBearer())]


# User endpoints
@router.post(
    "/",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new order (user)",
)
async def create_order(
    db: DbSession,
    token_data: AccessToken,
):
    return await OrderService.create_order(db, UUID(token_data.sub))


@router.get(
    "/me",
    response_model=List[OrderRead],
    summary="List my orders",
)
async def list_my_orders(
    db: DbSession,
    token_data: AccessToken,
):
    return await OrderService.list_orders_by_user(db, UUID(token_data.sub))


@router.get(
    "/me/{order_id}",
    response_model=OrderRead,
    summary="Get my order by ID",
)
async def get_my_order_by_id(
    order_id: UUID,
    db: DbSession,
    token_data: AccessToken,
):
    order = await OrderService.get_order_by_id(db, order_id)
    if not order or order.user_id != UUID(token_data.sub):
        raise HTTPException(status_code=404, detail="Order not found")
    return order


# Admin endpoints
@router.get(
    "/{order_id}",
    response_model=OrderRead,
    summary="Get order by ID (admin)",
    dependencies=[role_checker_admin],
)
async def admin_get_order(
    order_id: UUID,
    db: DbSession,
):
    order = await OrderService.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get(
    "/user/{user_id}",
    response_model=List[OrderRead],
    summary="List orders by user (admin)",
    dependencies=[role_checker_admin],
)
async def admin_list_orders_by_user(
    user_id: UUID,
    db: DbSession,
):
    return await OrderService.list_orders_by_user(db, user_id)


@router.patch(
    "/{order_id}/status",
    response_model=OrderRead,
    summary="Update order status (admin)",
    dependencies=[role_checker_admin],
)
async def admin_update_order_status(
    order_id: UUID,
    order_status: OrderStatusUpdate,
    db: DbSession,
):
    order = await OrderService.update_order_status(db, order_id, order_status.status)
    return order
