from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, status

from sqlmodel.ext.asyncio.session import AsyncSession

from app.database.core import get_session
from app.modules.auth.dependencies import AccessToken
from app.modules.users.schemas import (
    PasswordUpdate,
    UserRead,
    UserReadDetail,
    UserUpdate,
)
from app.modules.users.service import UserService


router = APIRouter(prefix="/api/v1/users/me", tags=["Accounts"])

DbSession = Annotated[AsyncSession, Depends(get_session)]


@router.get("/", response_model=UserReadDetail)
async def get_my_account(token_data: AccessToken) -> UserReadDetail:
    return await UserService.get_user(UUID(token_data.sub))


@router.patch("/", response_model=UserRead)
async def update_my_account(
    db_session: DbSession, token_data: AccessToken, user_update: UserUpdate
) -> UserRead:
    return await UserService.update_user(db_session, UUID(token_data.sub), user_update)


@router.patch("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_my_password(
    db_session: DbSession, token_data: AccessToken, password_data: PasswordUpdate
) -> None:
    await UserService.change_user_password(
        db_session, UUID(token_data.sub), password_data
    )


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_account(db_session: DbSession, token_data: AccessToken) -> None:
    await UserService.delete_user(db_session, UUID(token_data.sub))
