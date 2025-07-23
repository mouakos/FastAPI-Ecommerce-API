from src.auth.schemas import TokenResponse, UserCreate, UserLogin, UserRead
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
import logging
from src.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from src.models.user import User
from .utils import get_user_token, verify_password, generate_password_hash


class AuthService:
    """AuthService class for handling user authentication operations."""

    @staticmethod
    async def login(db: AsyncSession, login_data: UserLogin) -> TokenResponse:
        """
        User login service.

        Args:
            db (AsyncSession): Database session.
            login_data (UserLogin): User login data.

        Returns:
            TokenResponse: User login token.
        """
        user = (
            await db.exec(select(User).where(User.email == login_data.email))
        ).first()
        if not user or not verify_password(login_data.password, user.password_hash):
            logging.warning(f"Failed login attempt for email: {login_data.email}")
            raise InvalidCredentialsError()
        return get_user_token(str(user.id))

    @staticmethod
    async def signup(db: AsyncSession, user_data: UserCreate) -> UserRead:
        """
        User signup service.

        Args:
            db (AsyncSession): Database session.
            user_data (UserCreate): User creation data.

        Returns:
            UserRead: Created user.
        """
        existing_user = (
            await db.exec(select(User).where(User.email == user_data.email))
        ).first()
        if existing_user:
            logging.warning(f"Signup attempt with existing email: {user_data.email}")
            raise UserAlreadyExistsError(user_data.email)
        user = User(
            **user_data.model_dump(),
            password_hash=generate_password_hash(user_data.password),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return UserRead(**user.model_dump())
