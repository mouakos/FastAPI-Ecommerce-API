from uuid import UUID
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from src.core.dependencies import DbSession, RoleChecker
from src.users.schemas import RoleUpdate, UserRead, UserRole, UserUpdate
from src.users.service import UserService

router = APIRouter(prefix="/api/v1/users", tags=["Users"])

role_checker_admin = Depends(RoleChecker([UserRole.admin]))


@router.get(
    "/",
    response_model=list[UserRead],
    status_code=status.HTTP_200_OK,
    summary="Get All Users",
    dependencies=[role_checker_admin],
)
async def get_all_users(db_session: DbSession) -> list[UserRead]:
    return await UserService.get_all_users(db_session)


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
    user_data: UserUpdate,
) -> UserRead:
    return await UserService.update_user(
        db_session, user_id, user_data.model_dump(exclude_unset=True)
    )


@router.patch(
    "/{user_id}/role-change",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary="Update User Role by ID",
    dependencies=[role_checker_admin],
)
async def change_user_role(
    db_session: DbSession,
    user_id: UUID,
    role_data: RoleUpdate,
) -> UserRead:
    # TODO - Avoid current user to change own role
    return await UserService.change_user_role(db_session, user_id, role_data)


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
