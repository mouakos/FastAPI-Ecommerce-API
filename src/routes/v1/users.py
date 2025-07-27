from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from src.core.dependencies import DbSession, RoleChecker
from src.users.schemas import (
    AdminUserUpdate,
    UserRead,
    UserRole,
)
from src.users.service import UserService
from src.utils.paginate import PaginatedResponse

router = APIRouter(prefix="/api/v1/users", tags=["Users"])

role_checker_admin = Depends(RoleChecker([UserRole.admin]))


@router.get(
    "/",
    response_model=PaginatedResponse[UserRead],
    status_code=status.HTTP_200_OK,
    summary="Get All Users",
    dependencies=[role_checker_admin],
)
async def get_all_users(
    db_session: DbSession,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, description="Number of users per page"),
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    search: Optional[str] = Query("", description="Search based email"),
) -> PaginatedResponse[UserRead]:
    return await UserService.get_all_users(
        db_session, page=page, page_size=page_size, search=search, role=role
    )


@router.get(
    "/{user_id}",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary="Get User by ID",
    dependencies=[role_checker_admin],
)
async def get_user(db_session: DbSession, user_id: UUID) -> UserRead:
    return await UserService.get_user(db_session, user_id)


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary="Update User by ID",
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
    summary="Delete User by ID",
    dependencies=[role_checker_admin],
)
async def delete_user(db_session: DbSession, user_id: UUID) -> JSONResponse:
    await UserService.delete_user(db_session, user_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "User deleted successfully"},
    )
