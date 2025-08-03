from typing import Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from datetime import timedelta, datetime

from app.utils.security import create_token, get_password_hash, verify_password
from app.config import settings
from app.exceptions import AuthenticationError, ConflictError
from app.models.user import User
from app.modules.users.schemas import UserCreate, UserRead
from .schemas import TokenData, UserLogin, TokenResponse


class AuthService:
    @staticmethod
    async def login(db: AsyncSession, login_data: UserLogin) -> TokenResponse:
        """
        User login service.

        Args:
            db (AsyncSession): Database session.
            login_data (UserLogin): User login data.

        Raises:
            AuthenticationError: If the email or password is invalid.

        Returns:
            TokenResponse: User login token.
        """
        user = await AuthService._get_user_by_email(db, login_data.email)
        if not user or not verify_password(login_data.password, user.password_hash):
            raise AuthenticationError("Invalid email or password.")

        return AuthService._generate_tokens(user.id, user.role)

    @staticmethod
    async def register_user(db: AsyncSession, user_data: UserCreate) -> UserRead:
        """
        Create a new user.
        Args:
            db (AsyncSession): Database session.
            user_data (UserCreate): User creation data.

        Raises:
            ConflictError: If a user with the same email already exists.

        Returns:
            UserRead: Created user.
        """

        existing_user = await AuthService._get_user_by_email(db, user_data.email)
        if existing_user:
            raise ConflictError(f"User with email {user_data.email} already exists.")

        user = User(
            **user_data.model_dump(),
            password_hash=get_password_hash(user_data.password),
        )
        user = await db.add(user)
        await db.commit()
        return user

    @staticmethod
    async def refresh_token(token_data: TokenData) -> TokenResponse:
        """
        Refresh access token using refresh token data.

        Args:
            token_data (TokenData): Token data.

        Raises:
            AuthenticationError: If the token is invalid or expired.

        Returns:
            TokenResponse: New access token and its expiration.
        """
        if datetime.fromtimestamp(token_data.exp) <= datetime.now():
            raise AuthenticationError("Invalid or expired token.")

        new_access_token = create_token(token_data.sub, token_data.role)
        return TokenResponse(
            access_token=new_access_token,
            access_token_expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_SECONDS,
        )

    @staticmethod
    def _generate_tokens(user_id: str, role: str) -> TokenResponse:
        """
        Generate access and refresh tokens.

        Args:
            user_id (str): User ID.
            role (str): User role.

        Returns:
            TokenResponse: Tokens and expiration details.
        """
        access_token = create_token(user_id, role)
        refresh_token = create_token(
            user_id,
            role,
            timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
            refresh=True,
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            access_token_expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_SECONDS,
        )

    @staticmethod
    async def _get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """
        Get user by email.

        Args:
            db (AsyncSession): Database session.
            email (str): User email.

        Returns:
            UserRead: User data or None if not found.
        """
        user = (await db.exec(select(User).where(User.email == email))).first()
        return user
