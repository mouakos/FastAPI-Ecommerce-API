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


class CategoryNotFound(BaseApiError):
    """Category with the given ID does not exist"""

    pass


class CategoryAlreadyExists(BaseApiError):
    """Category with the given name already exists"""

    pass


class ProductNotFound(BaseApiError):
    """Product with the given ID does not exist"""

    pass


class ProductAlreadyExists(BaseApiError):
    """Product with the given SKU already exists"""

    pass


class CategoryHasProducts(BaseApiError):
    """Category has associated products and cannot be deleted"""

    pass


class TagNotFound(BaseApiError):
    """Tag with the given ID does not exist"""

    pass


class TagAlreadyExists(BaseApiError):
    """Tag with the given name already exists"""

    pass


class ReviewNotFound(BaseApiError):
    """Review with the given ID does not exist"""

    pass
