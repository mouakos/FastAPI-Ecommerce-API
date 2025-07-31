from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, status

from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.schemas import TokenData
from app.users.schemas import PasswordUpdate, UserRead, UserReadDetail, UserUpdate
from app.users.service import UserService
from app.auth.dependencies import AccessTokenBearer
from app.database.core import get_session

router = APIRouter(prefix="/api/v1/users/me", tags=["Accounts"])

DbSession = Annotated[AsyncSession, Depends(get_session)]
AccessToken = Annotated[TokenData, Depends(AccessTokenBearer())]


@router.get(
    "/", response_model=UserReadDetail, summary="Get current user's account details"
)
async def get_my_account(token_data: AccessToken) -> UserReadDetail:
    return await UserService.get_user_by_id(UUID(token_data.sub))


@router.patch(
    "/", response_model=UserRead, summary="Update current user's account details"
)
async def update_my_account(
    db_session: DbSession, token_data: AccessToken, user_update: UserUpdate
) -> UserRead:
    return await UserService.update_user(db_session, UUID(token_data.sub), user_update)


@router.patch(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change current user's password",
)
async def change_my_password(
    db_session: DbSession, token_data: AccessToken, password_data: PasswordUpdate
) -> None:
    await UserService.change_user_password(
        db_session, UUID(token_data.sub), password_data
    )


@router.delete(
    "/", status_code=status.HTTP_204_NO_CONTENT, summary="Delete current user's account"
)
async def delete_my_account(db_session: DbSession, token_data: AccessToken) -> None:
    await UserService.delete_user(db_session, UUID(token_data.sub))
