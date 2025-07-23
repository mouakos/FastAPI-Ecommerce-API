from uuid import UUID
from typing_extensions import Annotated
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.users.schemas import RoleUpdate, UserRead, UserUpdate
from src.users.service import UserService
from src.core.security import CurrentAdminUser
from src.database.core import get_session

router = APIRouter(prefix="/api/v1/users", tags=["Users"])

DbSession = Annotated[AsyncSession, Depends(get_session)]


@router.get(
    "/",
    response_model=list[UserRead],
    status_code=status.HTTP_200_OK,
    summary="Get All Users. Requires Admin Role",
)
async def get_all_users(
    db_session: DbSession, current_user: CurrentAdminUser
) -> list[UserRead]:
    return await UserService.get_all_users(db_session)


@router.get(
    "/{user_id}",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary="Get User by ID. Requires Admin Role",
)
async def get_user(
    db_session: DbSession, current_user: CurrentAdminUser, user_id: str
) -> UserRead:
    user_id = UUID(user_id)
    return await UserService.get_user(db_session, user_id)


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary="Update User by ID. Requires Admin Role",
)
async def update_user(
    db_session: DbSession,
    current_user: CurrentAdminUser,
    user_id: str,
    user_data: UserUpdate,
) -> UserRead:
    user_id = UUID(user_id)
    return await UserService.update_user(
        db_session, user_id, user_data.model_dump(exclude_unset=True)
    )


@router.patch(
    "/{user_id}/role-change",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary="Update User Role by ID. Requires Admin Role",
)
async def change_user_role(
    db_session: DbSession,
    current_user: CurrentAdminUser,
    user_id: str,
    role_data: RoleUpdate,
) -> UserRead:
    user_id = UUID(user_id)
    return await UserService.change_user_role(db_session, user_id, role_data)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete User by ID. Requires Admin Role",
)
async def delete_user(
    db_session: DbSession, current_user: CurrentAdminUser, user_id: str
) -> None:
    user_id = UUID(user_id)
    await UserService.delete_user(db_session, user_id)
