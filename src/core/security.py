import logging
from typing import Optional
from uuid import uuid4
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta

from .config import settings

passwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# TODO -- This should be replaced with a proper database or cache in production (e.g., Redis)
token_blocklist = set()


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


def create_token(
    user_id: str, expires_delta: timedelta = None, refresh: bool = False
) -> str:
    """Create a token with optional expiration.

    Args:
        token_data (TokenData): The data to encode in the token.
        expires_delta (timedelta, optional): The expiration time for the token. Defaults to None.
        refresh_token (bool): Whether the token is a refresh token.

    Returns:
        str: The encoded token.
    """
    payload = {"sub": user_id, "jti": str(uuid4()), "refresh": refresh}
    payload["exp"] = datetime.now() + (
        expires_delta or timedelta(seconds=settings.JWT_ACCESS_TOKEN_EXPIRE_SECONDS)
    )
    token = jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return token


def decode_access_token(token: str) -> Optional[dict]:
    """Decode an access token to extract the payload.

    Args:
        token (str): The access token to decode.

    Returns:
        Optional[dict]: The decoded token data if successful, None otherwise.
    """
    try:
        token_data = jwt.decode(
            token, key=settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return token_data
    except JWTError as e:
        logging.error(f"Token decoding failed: {e}")
        return None
