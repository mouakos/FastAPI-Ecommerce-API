import logging
from typing import Optional
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from typing_extensions import Annotated
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone


from src.users.schemas import TokenData, TokenResponse
from .config import settings
from .exceptions import InvalidTokenError, UnauthorizedError

passwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def generate_password_hash(password: str) -> str:
    """Generate a hashed password using bcrypt.

    Args:
        password (str): The password to hash.

    Returns:
        str: The hashed password.
    """
    hash = passwd_context.hash(password)
    return hash


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against a hashed password.

    Args:
        password (str): The password to verify.
        hashed_password (str): The hashed password to compare against.

    Returns:
        bool: True if the password is valid, False otherwise.
    """
    return passwd_context.verify(password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:
    """Create an access token with optional expiration.

    Args:
        data (dict): The data to encode in the token.
        expires_delta (Optional[int]): The expiration time in seconds.

    Returns:
        str: The encoded access token.
    """
    payload = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    payload.update({"exp": expire})
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token


def get_user_token(token_data: TokenData) -> TokenResponse:
    """Get a user token for a specific user.

    Args:
        token_data (TokenData): The token data containing user ID and role.

    Returns:
        TokenResponse: A TokenResponse containing the access token, token type, and expiration time.
    """
    access_token_expiry = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={"sub": token_data.user_id, "role": token_data.role},
        expires_delta=access_token_expiry,
    )
    return TokenResponse(access_token=token, expires_in=access_token_expiry.seconds)


def verify_token(token: str) -> TokenData:
    """Verify a JWT token and return the token data.

    Args:
        token (str): The JWT token to verify.

    Raises:
        InvalidTokenError: If the token is invalid or expired.

    Returns:
        TokenData: The decoded token data.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        return TokenData(user_id=user_id, role=role)
    except JWTError as e:
        logging.warning(f"Token verification failed: {str(e)}")
        raise InvalidTokenError()


def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]) -> TokenData:
    return verify_token(token)


CurrentUser = Annotated[TokenData, Depends(get_current_user)]


def get_admin_user(current_user: CurrentUser) -> TokenData:
    if current_user.role != "admin":
        raise UnauthorizedError()
    return current_user


CurrentAdminUser = Annotated[TokenData, Depends(get_admin_user)]
