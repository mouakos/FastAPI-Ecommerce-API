from typing import Optional
import uuid
import logging
from fastapi.params import Depends
from typing_extensions import Annotated
from fastapi import Request
from fastapi.security import HTTPBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.security import decode_access_token, token_blocklist
from app.database.core import get_session
from app.users.service import UserService
from app.users.schemas import UserRead, UserRole
from app.core.exceptions import (
    AccessTokenRequired,
    InsufficientPermission,
    InvalidToken,
    RefreshTokenRequired,
    RevokedToken,
)


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)
        self.auto_error = auto_error

    async def __call__(self, request: Request) -> Optional[dict]:
        """Extract and decode the token from the request.
        Args:
            request (Request): The incoming request.
        Raises:
            InvalidToken: If the token is invalid or expired.
            RevokedToken: If the token has been revoked.
        Returns:
            Optional[dict]: The decoded token data if valid, None otherwise.
        """
        credentials = await super().__call__(request)

        token = credentials.credentials

        token_data = decode_access_token(token)

        if token_data.get("jti") in token_blocklist:
            logging.warning(f"Revoked token used: {token_data.get('jti')}")
            raise RevokedToken()

        if not token_data:
            raise InvalidToken()

        self.verify_token_data(token_data)

        return token_data

    def verify_token_data(self, token_data: dict) -> None:
        """Verify the token data.
        This method should be overridden in subclasses to implement specific token verification logic.

        Args:
            token_data (dict): The decoded token data.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError("please override this method in the subclass")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        """Verify the access token data.

        Args:
            token_data (dict): The decoded token data.

        Raises:
            AccessTokenRequired: If the token data does not contain 'access'.
        """
        if token_data and token_data.get("refresh"):
            logging.warning("Access token used with refresh token data")
            raise AccessTokenRequired()


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        """Verify the refresh token data.

        Args:
            token_data (dict): The decoded token data.

        Raises:
            RefreshTokenRequired: If the token data does not contain 'refresh'.
        """
        if not token_data or not token_data.get("refresh"):
            logging.warning("Refresh token used with access token data")
            raise RefreshTokenRequired()


DbSession = Annotated[AsyncSession, Depends(get_session)]


async def get_current_user(
    token: Annotated[dict, Depends(AccessTokenBearer())],
    db_session: DbSession,
) -> UserRead:
    """Get the current user based on the access token.

    Args:
        token (Annotated[dict, Depends): The decoded access token data.
        db_session (DbSession): The database session.

    Returns:
        UserRead: The current user.
    """
    user_id = token.get("sub")
    return await UserService.get_user(db_session, uuid.UUID(user_id))


CurrentUser = Annotated[UserRead, Depends(get_current_user)]


class RoleChecker:
    def __init__(self, allowed_roles: list[UserRole]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: UserRead = Depends(get_current_user)) -> bool:
        """Check if the current user has one of the allowed roles.
        Args:
            current_user (UserRead): The current user.
        Raises:
            InsufficientPermission: If the user does not have sufficient permissions.
        Returns:
            bool: True if the user has sufficient permissions, False otherwise.
        """
        if current_user.role in self.allowed_roles:
            return True
        logging.warning(f"User {current_user.id} does not have sufficient permissions")
        raise InsufficientPermission()
