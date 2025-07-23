from typing_extensions import Annotated
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession


from src.users.schemas import PasswordUpdate, UserRead, AccountUpdate
from src.users.service import UserService
from src.core.security import CurrentUser
from src.database.core import get_session

router = APIRouter(prefix="/api/v1/me", tags=["Accounts"])

DbSession = Annotated[AsyncSession, Depends(get_session)]


@router.get(
    "/", response_model=UserRead, summary="Get current logged-in User Information"
)
async def get_account(db_session: DbSession, current_user: CurrentUser) -> UserRead:
    return await UserService.get_user(db_session, current_user.get_user_id())


@router.patch(
    "/", response_model=UserRead, summary="Update current logged-in User Information"
)
async def update_account(
    db_session: DbSession, current_user: CurrentUser, user_data: AccountUpdate
) -> UserRead:
    return await UserService.update_user(
        db_session, current_user.get_user_id(), user_data.model_dump(exclude_unset=True)
    )


@router.put(
    "/change-password",
    summary="Change Password of current logged-in User",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def change_password(
    db_session: DbSession, current_user: CurrentUser, password_data: PasswordUpdate
) -> None:
    await UserService.change_user_password(
        db_session, current_user.get_user_id(), password_data
    )


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete current logged-in User Account",
)
async def delete_account(db_session: DbSession, current_user: CurrentUser) -> None:
    await UserService.delete_user(db_session, current_user.get_user_id())
