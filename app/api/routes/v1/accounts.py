from fastapi import APIRouter, status

from app.users.schemas import PasswordUpdate, UserRead, UserUpdate
from app.users.service import UserService
from app.api.dependencies import CurrentUser, DbSession

router = APIRouter(prefix="/api/v1/me", tags=["Accounts"])


@router.get(
    "/", response_model=UserRead, summary="Get current logged-in User Information"
)
async def get_account(current_user: CurrentUser) -> UserRead:
    return current_user


@router.patch(
    "/", response_model=UserRead, summary="Update current logged-in User Information"
)
async def update_account(
    db_session: DbSession, current_user: CurrentUser, user_update: UserUpdate
) -> UserRead:
    return await UserService.update_user(db_session, current_user.id, user_update)


@router.patch(
    "/change-password",
    summary="Change Password of current logged-in User",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def change_password(
    db_session: DbSession, current_user: CurrentUser, password_data: PasswordUpdate
) -> None:
    await UserService.change_user_password(db_session, current_user.id, password_data)


@router.delete(
    "/",
    summary="Delete current logged-in User Account",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_account(db_session: DbSession, current_user: CurrentUser) -> None:
    await UserService.delete_user(db_session, current_user.id)
