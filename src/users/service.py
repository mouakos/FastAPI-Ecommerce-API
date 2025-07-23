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
from src.core.security import generate_password_hash, get_user_token, verify_password
from src.core.exceptions import (
    InvalidCredentialsError,
    InvalidPasswordError,
    PasswordMismatchError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from src.models.user import User


class UserService:

    @staticmethod
    async def get_all_users(db_session: AsyncSession) -> list[UserRead]:
        """Retrieve all users.

        Args:
            db_session (AsyncSession): Database session for querying.

        Returns:
            list[UserRead]: A list of all users.
        """
        users = await db_session.exec(select(User).order_by(User.created_at()))
        return [UserRead.model_validate(user) for user in users.all()]

    @staticmethod
    async def get_user(db_session: AsyncSession, user_id: UUID) -> UserRead:
        """Retrieve a user by their ID.

        Args:
            db_session (AsyncSession): Database session for querying.
            user_id (UUID): User ID to retrieve.

        Raises:
            UserNotFoundError: If the user is not found.

        Returns:
            UserRead: The retrieved user.
        """
        user = await db_session.get(User, user_id)
        if not user:
            logging.error(f"User with ID {user_id} not found")
            raise UserNotFoundError(user_id)
        logging.info(f"User with ID {user_id} retrieved successfully")
        return UserRead(**user.model_dump())

    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> UserRead:
        """
        Create a new user.

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
            UserNotFoundError: If the user is not found.

        Returns:
            UserRead: The updated user.
        """
        user = await db_session.get(User, user_id)
        if not user:
            logging.error(f"User with ID {user_id} not found for update")
            raise UserNotFoundError(user_id)

        for key, value in user_data.items():
            setattr(user, key, value)

        db_session.add(user)
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
            UserNotFoundError: If the user is not found.
        """
        user = await db_session.get(User, user_id)
        if not user:
            logging.error(f"User with ID {user_id} not found for deletion")
            raise UserNotFoundError(user_id)

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

        Returns:
            TokenResponse: User login token.
        """
        user = (
            await db.exec(select(User).where(User.email == login_data.email))
        ).first()
        if not user or not verify_password(login_data.password, user.password_hash):
            logging.warning(f"Failed login attempt for email: {login_data.email}")
            raise InvalidCredentialsError()
        return get_user_token(str(user.id), user.role.value)

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
            UserNotFoundError: If the user is not found.

        Returns:
            UserRead: The updated user with the new password.
        """
        user = await db_session.get(User, user_id)
        if not user:
            logging.error(f"User with ID {user_id} not found for password change")
            raise UserNotFoundError(user_id)

        # Verify current password
        if not verify_password(password_data.current_password, user.password):
            logging.error(f"Current password for user with ID {user_id} is incorrect")
            raise InvalidPasswordError()

        # Verify new passwords match
        if password_data.new_password != password_data.new_password_confirm:
            logging.warning(
                f"Password mismatch during change attempt for user ID: {user_id}"
            )
            raise PasswordMismatchError()

        user.password_hash = generate_password_hash(password_data.new_password)
        await db_session.commit()
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
            UserNotFoundError: If the user is not found.

        Returns:
            UserRead: The updated user with the new role.
        """
        user = await db_session.get(User, user_id)
        if not user:
            logging.error(f"User with ID {user_id} not found for role change")
            raise UserNotFoundError(user_id)

        user.role = role_data.role.value
        await db_session.commit()
        await db_session.refresh(user)
        logging.info(
            f"Role for user with ID {user_id} changed to {role_data.role.value} successfully"
        )
        return UserRead(**user.model_dump())
