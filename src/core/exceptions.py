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
    """Category with the given name or slug already exists"""

    pass


class ParentCategoryNotFound(BaseApiError):
    """Parent category with the given ID does not exist"""

    pass


class InvalidCategoryHierarchy(BaseApiError):
    """Category cannot be its own parent or a parent of itself indirectly"""

    pass


class CategoryHasChildren(BaseApiError):
    """Category has child categories and cannot be deleted"""

    pass
