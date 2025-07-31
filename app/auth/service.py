from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from datetime import timedelta, datetime

from app.exceptions import AuthenticationError, ConflictError
from app.auth.schemas import TokenData, UserLogin, TokenResponse
from app.models.user import User
from app.users.schemas import UserCreate, UserRead
from app.utils.security import create_token, generate_password_hash, verify_password
from app.config import settings


class AuthService:
    @staticmethod
    async def login(db: AsyncSession, login_data: UserLogin) -> TokenResponse:
        """
        User login service.

        Args:
            db (AsyncSession): Database session.
            login_data (UserLogin): User login data.

        raises:
            AuthenticationError: If the email or password is invalid.

        Returns:
            TokenResponse: User login token.
        """
        user = (
            await db.exec(select(User).where(User.email == login_data.email))
        ).first()
        if not user or not verify_password(login_data.password, user.password_hash):
            raise AuthenticationError("Invalid email or password.")
        
        access_token = create_token(str(user.id), user.role.value)
        refresh_token = create_token(
            str(user.id),
            user.role.value,
            timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
            refresh=True,
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            access_token_expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_SECONDS,
        )

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

        existing_user = await (
            await db.exec(select(User).where(User.email == user_data.email))
        ).first()
        if existing_user:
            raise ConflictError(f"User with email {user_data.email} already exists.")
        
        user = User(
            **user_data.model_dump(),
            password_hash=generate_password_hash(user_data.password),
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
        user_id = token_data.sub
        role = token_data.role
        expiry_timestamp = token_data.exp
        if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
            new_access_token = create_token(user_id, role)
            return TokenResponse(
                access_token=new_access_token,
                access_token_expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_SECONDS,
            )
        raise AuthenticationError("Invalid or expired token.")
