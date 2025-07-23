from typing import Optional
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone


from src.auth.schemas import TokenResponse
from src.config import settings

passwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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


def get_user_token(user_id: str) -> TokenResponse:
    """Get a user token for a specific user.

    Args:
        user_id (str): The ID of the user.

    Returns:
        TokenResponse: A TokenResponse containing the access token, token type, and expiration time.
    """
    access_token_expiry = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={"sub": user_id}, expires_delta=access_token_expiry
    )
    return TokenResponse(
        access_token=token, expires_in=access_token_expiry.seconds
    )
