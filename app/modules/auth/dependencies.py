from typing import Optional
import logging
from typing_extensions import Annotated
from fastapi import Depends, Request
from fastapi.security import HTTPBearer

from app.utils.security import decode_access_token, token_blocklist
from app.exceptions import AuthorizationError, AuthenticationError
from .schemas import TokenData


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

        data = decode_access_token(token)

        token_data = TokenData(**data)
        if not token_data.is_valid():
            logging.warning("Invalid token")
            raise AuthenticationError("Invalid or expired token provided.")

        if token_data.jti in token_blocklist:
            logging.warning(f"Revoked token used: {token_data.jti}")
            raise AuthenticationError("Token has been revoked.")

        self.verify_token_data(token_data)

        return token_data

    def verify_token_data(self, token_data: TokenData) -> None:
        """Verify the token data.
        This method should be overridden in subclasses to implement specific token verification logic.

        Args:
            token_data (TokenData): The decoded token data.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError("please override this method in the subclass")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: TokenData) -> None:
        """Verify the access token data.

        Args:
            token_data (TokenData): The decoded token data.

        Raises:
            AccessTokenRequired: If the token data does not contain 'access'.
        """
        if token_data.refresh:
            logging.warning("Access token used with refresh token data")
            raise AuthenticationError("Access token is required.")


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: TokenData) -> None:
        """Verify the refresh token data.

        Args:
            token_data (TokenData): The decoded token data.

        Raises:
            RefreshTokenRequired: If the token data does not contain 'refresh'.
        """
        if not token_data.refresh:
            logging.warning("Refresh token used with access token data")
            raise AuthenticationError("Refresh token is required.")


AccessToken = Annotated[TokenData, Depends(AccessTokenBearer())]


class RoleChecker:
    def __init__(self, allowed_roles: list[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(
        self, token_data: Annotated[TokenData, Depends(AccessTokenBearer())]
    ) -> bool:
        """Check if the current user has one of the allowed roles.
        Args:
            current_user (UserRead): The current user.
        Raises:
            AuthorizationError: If the user does not have sufficient permissions.
        Returns:
            bool: True if the user has sufficient permissions, False otherwise.
        """
        if token_data.role in self.allowed_roles:
            return True
        logging.warning(f"User {token_data.sub} does not have sufficient permissions")
        raise AuthorizationError("Insufficient permissions to access this resource.")
