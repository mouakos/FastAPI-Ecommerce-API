class BaseApiError(Exception):
    """Base class for all API errors"""

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


class CategoryHasProducts(BaseApiError):
    """Category has associated products and cannot be deleted"""

    pass


class InsufficientStock(BaseApiError):
    """Insufficient stock for the product"""

    pass


class ApiException(Exception):
    """Base class for API exceptions"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(ApiException):
    """Resource not found"""

    def __init__(self, message: str):
        super().__init__(message=message)


class ConflictError(ApiException):
    """Resource already exists"""

    def __init__(self, message: str):
        super().__init__(message=message)


class PasswordMismatchError(ApiException):
    """Password does not match"""

    def __init__(self):
        super().__init__(message="Passwords do not match")


class InvalidPasswordError(ApiException):
    """Invalid password provided"""

    def __init__(self):
        super().__init__(message="Invalid password provided")


class AuthenticationError(ApiException):
    """Authentication failed"""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message=message)


class AuthorizationError(ApiException):
    """Authorization failed"""

    def __init__(
        self, message: str = "You do not have permission to perform this action"
    ):
        super().__init__(message=message)


class InvalidTokenError(ApiException):
    """Invalid or expired token provided"""

    def __init__(self, message: str = "Invalid or expired token provided"):
        super().__init__(message=message)


class BadRequestError(ApiException):
    """Bad request error"""

    def __init__(self, message: str = "Bad request"):
        super().__init__(message=message)
