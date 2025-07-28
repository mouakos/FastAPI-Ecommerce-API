from datetime import datetime, timedelta
from math import ceil
from typing import Optional
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
import logging
from uuid import UUID
from src.users.schemas import (
    PasswordUpdate,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserRead,
    UserUpdate,
)
from src.core.security import (
    create_token,
    generate_password_hash,
    verify_password,
)
from src.core.exceptions import (
    InvalidPassword,
    InvalidToken,
    PasswordMismatch,
    UserAlreadyExists,
    UserNotFound,
    InvalidCredentials,
)
from src.models.user import User, UserRole
from src.core.config import settings
from src.utils.paginate import PaginatedResponse


class UserService:
    @staticmethod
    async def get_all_users(
        db_session: AsyncSession,
        page: int,
        page_size: int,
        role: Optional[UserRole],
        is_active: Optional[bool],
        search: Optional[str],
    ) -> PaginatedResponse[UserRead]:
        """Retrieve all users with pagination and optional filters.

        Args:
            db_session (AsyncSession): Database session for querying.
            page (int): Page number for pagination.
            page_size (int): Number of users per page.
            role (Optional[UserRole]): Filter by user role.
            search (Optional[str]): Search term to filter users by email.

        Returns:
            PaginatedResponse[UserRead]: A paginated response containing user data.
        """
        # Get total count (without limit/offset)
        count_stmt = (
            select(func.count())
            .select_from(User)
            .where(
                (User.role == role) if role else True,
                (User.email.ilike(f"%{search}%")) if search else True,
                (User.is_active == is_active) if is_active is not None else True,
            )
        )
        total = (await db_session.exec(count_stmt)).one()

        # Get paginated users
        result = await db_session.exec(
            select(User)
            .where(
                (User.role == role) if role else True,
                (User.email.ilike(f"%{search}%")) if search else True,
                (User.is_active == is_active) if is_active is not None else True,
            )
            .order_by(User.created_at.desc())
            .limit(page_size)
            .offset((page - 1) * page_size)
        )
        users = result.all()

        return PaginatedResponse[UserRead](
            total=total,
            page=page,
            size=page_size,
            pages=ceil(total / page_size) if total else 1,
            items=[UserRead(**user.model_dump()) for user in users],
        )

    @staticmethod
    async def get_user(db_session: AsyncSession, user_id: UUID) -> UserRead:
        """Retrieve a user by their ID.

        Args:
            db_session (AsyncSession): Database session for querying.
            user_id (UUID): User ID to retrieve.

        Raises:
            UserNotFound: If the user is not found.

        Returns:
            UserRead: The retrieved user.
        """
        user = await db_session.get(User, user_id)
        if not user:
            logging.error(f"User with ID {user_id} not found")
            raise UserNotFound(user_id)
        logging.info(f"User with ID {user_id} retrieved successfully")
        return UserRead(**user.model_dump())

    @staticmethod
    async def create_user(db_session: AsyncSession, user_data: UserCreate) -> UserRead:
        """
        Create a new user.

        Args:
            db_session (AsyncSession): Database session.
            user_data (UserCreate): User creation data.

        Raises:
            UserAlreadyExists: If a user with the same email already exists.

        Returns:
            UserRead: Created user.
        """

        existing_user = (
            await db_session.exec(select(User).where(User.email == user_data.email))
        ).first()
        if existing_user:
            logging.warning(f"Signup attempt with existing email: {user_data.email}")
            raise UserAlreadyExists()
        user = User(
            **user_data.model_dump(),
            password_hash=generate_password_hash(user_data.password),
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        logging.info(f"User {user.email} created successfully")
        return UserRead(**user.model_dump())

    @staticmethod
    async def update_user(
        db_session: AsyncSession, user_id: UUID, data: UserUpdate
    ) -> UserRead:
        """Update a user's information.

        Args:
            db_session (AsyncSession): Database session for querying.
            user_id (UUID): User ID to update.
            user_data (dict): Data to update the user with.

        Raises:
            UserNotFound: If the user is not found.

        Returns:
            UserRead: The updated user.
        """

        user = await db_session.get(User, user_id)
        if not user:
            logging.error(f"User with ID {user_id} not found for update")
            raise UserNotFound(user_id)

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(user, key, value)

        # TODO - Check if fields are actually changed
        user.updated_at = datetime.utcnow()

        await db_session.commit()
        await db_session.refresh(user)
        logging.info(f"User with ID {user_id} updated successfully")
        return UserRead(**user.model_dump())

    @staticmethod
    async def delete_user(db_session: AsyncSession, user_id: UUID) -> None:
        """Delete a user by their ID.

        Args:
            db_session (AsyncSession): Database session for querying.
            user_id (UUID): User ID to delete.

        Raises:
            UserNotFound: If the user is not found.
        """
        user = await db_session.get(User, user_id)
        if not user:
            logging.error(f"User with ID {user_id} not found for deletion")
            raise UserNotFound(user_id)

        await db_session.delete(user)
        await db_session.commit()
        logging.info(f"User with ID {user_id} deleted successfully")

    @staticmethod
    async def login(db: AsyncSession, login_data: UserLogin) -> TokenResponse:
        """
        User login service.

        Args:
            db (AsyncSession): Database session.
            login_data (UserLogin): User login data.

        raises:
            InvalidCredentials: If the email or password is invalid.

        Returns:
            TokenResponse: User login token.
        """
        user = (
            await db.exec(select(User).where(User.email == login_data.email))
        ).first()
        if not user or not verify_password(login_data.password, user.password_hash):
            logging.warning(f"Failed login attempt for email: {login_data.email}")
            raise InvalidCredentials()
        access_token = create_token(str(user.id))
        refresh_token = create_token(
            str(user.id),
            timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
            refresh=True,
        )
        logging.info(f"User {user.email} logged in successfully")
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            access_token_expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_SECONDS,
        )

    @staticmethod
    async def change_user_password(
        db_session: AsyncSession, user_id: UUID, password_data: PasswordUpdate
    ) -> None:
        """Change a user's password.

        Args:
            db_session (AsyncSession): Database session for querying.
            user_id (UUID): User ID to change the password for.
            password_data (PasswordChange): Data containing the new password.

        Raises:
            UserNotFound: If the user is not found.
            InvalidPassword: If the current password is incorrect.
            PasswordMismatch: If the new password and confirmation do not match.

        Returns:
            UserRead: The updated user with the new password.
        """
        user = await db_session.get(User, user_id)
        if not user:
            logging.error(f"User with ID {user_id} not found for password change")
            raise UserNotFound(user_id)

        # Verify current password
        if not verify_password(password_data.current_password, user.password):
            logging.error(f"Current password for user with ID {user_id} is incorrect")
            raise InvalidPassword()

        # Verify new passwords match
        if password_data.new_password != password_data.new_password_confirm:
            logging.warning(
                f"Password mismatch during change attempt for user ID: {user_id}"
            )
            raise PasswordMismatch()

        user.password_hash = generate_password_hash(password_data.new_password)
        user.updated_at = datetime.utcnow()
        await db_session.commit()
        await db_session.refresh(user)
        logging.info(f"Password for user with ID {user_id} changed successfully")

    @staticmethod
    async def refresh_token(token_data: dict) -> TokenResponse:
        """Refresh the access token if it is still valid.

        Args:
            token_data (dict): Data containing the token information.

        Raises:
            InvalidToken: If the token is invalid or expired.

        Returns:
            TokenResponse: The response containing the new access token and its expiration time.
        """
        expiry_timestamp = token_data.get("exp")
        if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
            new_access_token = create_token(token_data.get("sub"))
            return TokenResponse(
                access_token=new_access_token,
                access_token_expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_SECONDS,
            )
        return InvalidToken()
