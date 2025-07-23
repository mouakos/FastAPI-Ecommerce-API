class BaseApiError(Exception):
    """Base class for all API errors"""

    pass


class UserNotFound(BaseApiError):
    """User with the given email does not exist"""

    pass


class UserAlreadyExists(BaseApiError):
    """User with the given email already exists"""

    pass


class InvalidToken(BaseApiError):
    """User has provided an invalid or expired token"""

    pass


class RevokedToken(BaseApiError):
    """User has provided a token that has been revoked"""

    pass


class AccessTokenRequired(BaseApiError):
    """User has provided a refresh token when an access token is needed"""

    pass


class RefreshTokenRequired(BaseApiError):
    """User has provided an access token when a refresh token is needed"""

    pass


class InsufficientPermission(BaseApiError):
    """User does not have the necessary permissions to perform an action."""

    pass


class PasswordMismatch(BaseApiError):
    """User has provided passwords that do not match."""

    pass


class InvalidPassword(BaseApiError):
    """User has provided an invalid password"""

    pass


class InvalidCredentials(BaseApiError):
    """User has provided invalid credentials for login"""

    pass
