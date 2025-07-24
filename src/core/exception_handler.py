from typing import Any, Callable
from fastapi import Request, status, FastAPI
from fastapi.responses import JSONResponse
import logging

from src.core.exceptions import (
    AccessTokenRequired,
    BaseApiError,
    CategoryAlreadyExists,
    CategoryNotFound,
    InsufficientPermission,
    InvalidCredentials,
    InvalidPassword,
    InvalidToken,
    PasswordMismatch,
    ProductAlreadyExists,
    ProductNotFound,
    RefreshTokenRequired,
    RevokedToken,
    UserAlreadyExists,
    UserNotFound,
)


def create_exception_handler(
    status_code: int, initial_detail: Any
) -> Callable[[Request, Exception], JSONResponse]:
    async def exception_handler(request: Request, exc: BaseApiError) -> JSONResponse:
        return JSONResponse(content=initial_detail, status_code=status_code)

    return exception_handler


def register_all_errors(app: FastAPI):
    app.add_exception_handler(
        UserAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            initial_detail={
                "message": "User with email already exists",
                "error_code": "user_exists",
            },
        ),
    )

    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "User not found",
                "error_code": "user_not_found",
            },
        ),
    )
    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "The provided email or password is invalid",
                "error_code": "invalid_email_or_password",
            },
        ),
    )
    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token is invalid or expired",
                "resolution": "Please get new token",
                "error_code": "invalid_token",
            },
        ),
    )
    app.add_exception_handler(
        RevokedToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token is invalid or has been revoked",
                "resolution": "Please get new token",
                "error_code": "token_revoked",
            },
        ),
    )
    app.add_exception_handler(
        AccessTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Access token is required for this action",
                "resolution": "Please provide a valid access token or get a new one",
                "error_code": "access_token_required",
            },
        ),
    )
    app.add_exception_handler(
        RefreshTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "The provided token is not a refresh token",
                "resolution": "Please provide a valid refresh token or get a new one",
                "error_code": "refresh_token_required",
            },
        ),
    )
    app.add_exception_handler(
        InsufficientPermission,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "You do not have enough permissions to perform this action",
                "error_code": "insufficient_permissions",
            },
        ),
    )
    app.add_exception_handler(
        PasswordMismatch,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Password mismatch",
                "resolution": "Please ensure the new password and confirmation match",
                "error_code": "password_mismatch",
            },
        ),
    )

    app.add_exception_handler(
        InvalidPassword,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Password is invalid",
                "error_code": "invalid_password",
            },
        ),
    )
    app.add_exception_handler(
        CategoryNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Category not found",
                "error_code": "category_not_found",
            },
        ),
    )

    app.add_exception_handler(
        CategoryAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            initial_detail={
                "message": "Category with this name already exists",
                "error_code": "category_already_exists",
            },
        ),
    )

    app.add_exception_handler(
        ProductNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Product not found",
                "error_code": "product_not_found",
            },
        ),
    )
    
    app.add_exception_handler(
        ProductAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            initial_detail={
                "message": "Product with this SKU already exists",
                "error_code": "product_already_exists",
            },
        ),
    )

    @app.exception_handler(status.HTTP_500_INTERNAL_SERVER_ERROR)
    async def internal_server_error(request, exc):
        logging.error(
            f"Internal Server Error: {exc}",
            extra={"request": request, "exception": exc},
        )
        return JSONResponse(
            content={
                "message": "Oops! Something went wrong",
                "error_code": "server_error",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
