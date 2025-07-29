from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from app.api.dependencies import DbSession, CurrentUser, RoleChecker
from app.orders.schemas import OrderRead, OrderStatusUpdate
from app.orders.service import OrderService
from app.users.schemas import UserRole

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])

role_checker_admin = Depends(RoleChecker([UserRole.admin]))


@router.post(
    "/",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new order",
)
async def checkout(
    db: DbSession,
    current_user: CurrentUser,
):
    return await OrderService.create_order(db, current_user.id)


@router.get("/me", response_model=OrderRead, summary="Get my order details")
async def get_my_order(
    db: DbSession,
    current_user: CurrentUser,
):
    return await OrderService.get_order_by_user(db, current_user.id)


@router.get(
    "/{order_id}",
    response_model=OrderRead,
    summary="Get order by ID",
    dependencies=[role_checker_admin],
)
async def get_order(
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
    summary="List orders by user",
    dependencies=[role_checker_admin],
)
async def list_orders_by_user(
    user_id: UUID,
    db: DbSession,
):
    return await OrderService.list_orders_by_user(db, user_id)


@router.patch(
    "/{order_id}/status",
    response_model=OrderRead,
    summary="Update order status",
    dependencies=[role_checker_admin],
)
async def update_order_status(
    order_id: UUID,
    order_status: OrderStatusUpdate,
    db: DbSession,
):
    order = await OrderService.update_order_status(db, order_id, order_status.status)
    return order
