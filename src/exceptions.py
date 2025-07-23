from fastapi import HTTPException, status


class UserError(HTTPException):
    """Base exception for user-related errors"""

    pass


class UserAlreadyExistsError(UserError):
    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email {email} already exists",
        )


class InvalidCredentialsError(UserError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid email or password"
        )
