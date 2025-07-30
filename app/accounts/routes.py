from fastapi import APIRouter, status

from app.users.schemas import PasswordUpdate, UserRead, UserReadDetail, UserUpdate
from app.users.service import UserService
from app.dependencies import CurrentUser, DbSession

router = APIRouter(prefix="/api/v1/users/me", tags=["Accounts"])


@router.get(
    "/", response_model=UserReadDetail, summary="Get current user's account details"
)
async def get_my_account(current_user: CurrentUser) -> UserReadDetail:
    return current_user


@router.patch(
    "/", response_model=UserRead, summary="Update current user's account details"
)
async def update_my_account(
    db_session: DbSession, current_user: CurrentUser, user_update: UserUpdate
) -> UserRead:
    return await UserService.update_user(db_session, current_user.id, user_update)


@router.patch(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change current user's password",
)
async def change_my_password(
    db_session: DbSession, current_user: CurrentUser, password_data: PasswordUpdate
) -> None:
    await UserService.change_user_password(db_session, current_user.id, password_data)


@router.delete(
    "/", status_code=status.HTTP_204_NO_CONTENT, summary="Delete current user's account"
)
async def delete_my_account(db_session: DbSession, current_user: CurrentUser) -> None:
    await UserService.delete_user(db_session, current_user.id)
