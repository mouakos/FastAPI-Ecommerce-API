from typing import Annotated, Literal, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.utils.paginate import PaginatedResponse
from app.database.core import get_session
from app.modules.auth.dependencies import RoleChecker
from .service import UserService
from .schemas import (
    AdminUserUpdate,
    UserRead,
    UserReadDetail,
)


router = APIRouter(prefix="/api/v1/users", tags=["Users"])

role_checker_admin = Depends(RoleChecker(["admin"]))

DbSession = Annotated[AsyncSession, Depends(get_session)]


@router.get(
    "/",
    response_model=PaginatedResponse[UserRead],
    dependencies=[role_checker_admin],
)
async def get_all_users(
    db_session: DbSession,
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(
        default=10, ge=1, le=100, description="Number of users per page"
    ),
    role: Optional[Literal["admin", "customer"]] = Query(
        default=None, description="Filter by user role"
    ),
    is_active: Optional[bool] = Query(
        default=None, description="Filter by active status"
    ),
    search: Optional[str] = Query(default="", description="Search based email"),
) -> PaginatedResponse[UserRead]:
    return await UserService.get_all_users(
        db_session,
        page=page,
        page_size=page_size,
        search=search,
        role=role,
        is_active=is_active,
    )


@router.get(
    "/{user_id}",
    response_model=UserReadDetail,
    dependencies=[role_checker_admin],
)
async def get_user(db_session: DbSession, user_id: UUID) -> UserReadDetail:
    return await UserService.get_user(db_session, user_id)


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    dependencies=[role_checker_admin],
)
async def update_user(
    db_session: DbSession,
    user_id: UUID,
    user_update: AdminUserUpdate,
) -> UserRead:
    return await UserService.update_user(db_session, user_id, user_update)


@router.delete(
    "/{user_id}",
    dependencies=[role_checker_admin],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(db_session: DbSession, user_id: UUID) -> None:
    await UserService.delete_user(db_session, user_id)
