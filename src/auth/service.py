from src.auth.schemas import TokenResponse, UserCreate, UserLogin, UserRead
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from fastapi import HTTPException, status

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
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid email or password",
            )
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
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        user = User(
            **user_data.model_dump(),
            password_hash=generate_password_hash(user_data.password),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return UserRead(**user.model_dump())
