from datetime import datetime, timedelta
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
import logging
from uuid import UUID
from src.users.schemas import (
    PasswordUpdate,
    RoleUpdate,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserRead,
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
from src.models.user import User
from src.core.config import settings


class UserService:
    @staticmethod
    async def get_all_users(db_session: AsyncSession) -> list[UserRead]:
        """Retrieve all users.

        Args:
            db_session (AsyncSession): Database session for querying.

        Returns:
            list[UserRead]: A list of all users.
        """
        users = await db_session.exec(select(User).order_by(User.full_name))
        return [UserRead(**user.model_dump()) for user in users.all()]

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
        async with db_session.begin():
            existing_user = (
                await db_session.exec(select(User).where(User.email == user_data.email))
            ).first()
            if existing_user:
                logging.warning(
                    f"Signup attempt with existing email: {user_data.email}"
                )
                raise UserAlreadyExists()
            user = User(
                **user_data.model_dump(),
                password_hash=generate_password_hash(user_data.password),
            )
            db_session.add(user)
        await db_session.refresh(user)
        logging.info(f"User {user.email} created successfully")
        return UserRead(**user.model_dump())

    @staticmethod
    async def update_user(
        db_session: AsyncSession, user_id: UUID, user_data: dict
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
        async with db_session.begin():
            user = await db_session.get(User, user_id)
            if not user:
                logging.error(f"User with ID {user_id} not found for update")
                raise UserNotFound(user_id)

            for key, value in user_data.items():
                setattr(user, key, value)

            user.updated_at = datetime.utcnow()

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
        async with db_session.begin():
            user = await db_session.get(User, user_id)
            if not user:
                logging.error(f"User with ID {user_id} not found for deletion")
                raise UserNotFound(user_id)

            await db_session.delete(user)
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
        async with db_session.begin():
            user = await db_session.get(User, user_id)
            if not user:
                logging.error(f"User with ID {user_id} not found for password change")
                raise UserNotFound(user_id)

            # Verify current password
            if not verify_password(password_data.current_password, user.password):
                logging.error(
                    f"Current password for user with ID {user_id} is incorrect"
                )
                raise InvalidPassword()

            # Verify new passwords match
            if password_data.new_password != password_data.new_password_confirm:
                logging.warning(
                    f"Password mismatch during change attempt for user ID: {user_id}"
                )
                raise PasswordMismatch()

            user.password_hash = generate_password_hash(password_data.new_password)
            user.updated_at = datetime.utcnow()

        await db_session.refresh(user)
        logging.info(f"Password for user with ID {user_id} changed successfully")

    @staticmethod
    async def change_user_role(
        db_session: AsyncSession, user_id: UUID, role_data: RoleUpdate
    ) -> UserRead:
        """Change a user's role.

        Args:
            db_session (AsyncSession): Database session for querying.
            user_id (UUID): User ID to change the role for.
            role_data (RoleChange): New role data to assign to the user.

        Raises:
            UserNotFound: If the user is not found.

        Returns:
            UserRead: The updated user with the new role.
        """
        async with db_session.begin():
            user = await db_session.get(User, user_id)
            if not user:
                logging.error(f"User with ID {user_id} not found for role change")
                raise UserNotFound(user_id)

            user.role = role_data.role.value
            user.updated_at = datetime.utcnow()

        await db_session.refresh(user)
        logging.info(
            f"Role for user with ID {user_id} changed to {role_data.role.value} successfully"
        )
        return UserRead(**user.model_dump())

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
