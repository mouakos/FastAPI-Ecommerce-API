from typing import Optional
import uuid
from fastapi.params import Depends
from typing_extensions import Annotated
from fastapi import Request
from fastapi.security import HTTPBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from src.core.security import decode_access_token
from src.database.core import get_session
from src.users.service import UserService
from src.users.schemas import UserRead, UserRole
from src.core.exceptions import (
    AccessTokenRequiredError,
    InsufficientPermissionError,
    InvalidTokenError,
    RefreshTokenRequiredError,
)


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)
        self.auto_error = auto_error

    async def __call__(self, request: Request) -> Optional[dict]:
        credentials = await super().__call__(request)

        token = credentials.credentials

        token_data = decode_access_token(token)

        if not token_data:
            raise InvalidTokenError()

        self.verify_token_data(token_data)

        return token_data

    def verify_token_data(self, token_data: dict) -> None:
        raise NotImplementedError("please override this method in the subclass")


class AccessTokenBearer(TokenBearer):

    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data.get("refresh"):
            raise AccessTokenRequiredError()


class RefreshTokenBearer(TokenBearer):

    def verify_token_data(self, token_data: dict) -> None:
        if not token_data or not token_data.get("refresh"):
            raise RefreshTokenRequiredError()


DbSession = Annotated[AsyncSession, Depends(get_session)]


async def get_current_user(
    token: Annotated[dict, Depends(AccessTokenBearer())],
    db_session: DbSession,
) -> UserRead:
    user_id = token.get("sub")
    return await UserService.get_user(db_session, uuid.UUID(user_id))


CurrentUser = Annotated[UserRead, Depends(get_current_user)]


class RoleChecker:
    def __init__(self, allowed_roles: list[UserRole]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: UserRead = Depends(get_current_user)) -> bool:

        if current_user.role in self.allowed_roles:
            return True

        raise InsufficientPermissionError()
