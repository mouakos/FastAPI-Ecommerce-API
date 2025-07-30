from datetime import timedelta
from typing import Optional
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func
from app.exceptions import (
    AuthenticationError,
    InvalidPasswordError,
    NotFoundError,
    PasswordMismatchError,
    ConflictError,
)

from app.users.schemas import (
    PasswordUpdate,
    UserCreate,
    UserLogin,
    UserRead,
    UserReadDetail,
    UserUpdate,
)
from app.utils.security import (
    TokenResponse,
    create_token,
    generate_password_hash,
    verify_password,
)
from app.models.user import User, UserRole
from app.config import settings
from app.utils.paginate import PaginatedResponse


class UserService:
    @staticmethod
    async def get_all_users(
        db: AsyncSession,
        page: int,
        page_size: int,
        role: Optional[UserRole],
        is_active: Optional[bool],
        search: Optional[str],
    ) -> PaginatedResponse[UserRead]:
        """Retrieve all users with pagination and optional filters.

        Args:
            db (AsyncSession): The database session.
            page (int): Page number for pagination.
            page_size (int): Number of users per page.
            role (Optional[UserRole]): Filter by user role.
            search (Optional[str]): Search term to filter users by email.

        Returns:
            PaginatedResponse[UserRead]: A paginated response containing user data.
        """
        stmt_count = (
            select(func.count())
            .select_from(User)
            .where(
                (User.role == role) if role else True,
                (User.is_active == is_active) if is_active is not None else True,
                (User.email.ilike(f"%{search}%")) if search else True,
            )
        )
        total = (await db.exec(stmt_count)).one()

        query = select(User).where(
            (User.role == role) if role else True,
            (User.is_active == is_active) if is_active is not None else True,
            (User.email.ilike(f"%{search}%")) if search else True,
        )
        result = await db.exec(query)
        users = result.all()
        return PaginatedResponse[UserRead](
            items=users[(page - 1) * page_size : page * page_size],
            total=total,
            page=page,
            page_size=page_size,
        )

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: UUID) -> UserReadDetail:
        """Retrieve a user by their ID.
        Args:ng.
            db (AsyncSession): The database session.
            user_id (UUID): User ID to retrieve.
        Raises:
            ResourceNotFoundError: If the user is not found.

        Returns:
            UserReadDetail: The retrieved user.
        """
        user = await db.get(User, user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")
        return user

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[UserRead]:
        """Retrieve a user by their email.

        Args:
            db (AsyncSession): The database session.
            email (str): The email of the user.

        Returns:
            Optional[UserRead]: The user if found, otherwise None.
        """
        return (await db.exec(select(User).where(User.email == email))).first()

    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> UserRead:
        """
        Create a new user.

        Args:
            user_data (UserCreate): User creation data.

        Raises:
            ConflictError: If a user with the same email already exists.

        Returns:
            UserRead: Created user.
        """

        existing_user = await UserService.get_user_by_email(db, user_data.email)
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
    async def update_user(
        db: AsyncSession, user_id: UUID, data: UserUpdate
    ) -> UserRead:
        """Update a user's information.

        Args:
            self (UserService): User service instance.
            user_id (UUID): User ID to update.
            user_data (dict): Data to update the user with.

        Raises:
            NotFoundError: If the user is not found.

        Returns:
            UserRead: The updated user.
        """

        user = await db.get(User, user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(user, key, value)

        await db.commit()
        return user

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: UUID) -> None:
        """Delete a user by their ID.

        Args:
            db (AsyncSession): Database session for querying.
            user_id (UUID): User ID to delete.

        Raises:
            NotFoundError: If the user is not found.
        """
        user = await db.get(User, user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")
        await db.delete(user)
        await db.commit()

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
        user = await UserService.get_user_by_email(db, login_data.email)
        if not user or not verify_password(login_data.password, user.password_hash):
            raise AuthenticationError("Invalid email or password.")
        access_token = create_token(str(user.id))
        refresh_token = create_token(
            str(user.id),
            timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
            refresh=True,
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            access_token_expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_SECONDS,
        )

    async def change_user_password(
        db: AsyncSession, user_id: UUID, password_data: PasswordUpdate
    ) -> None:
        """Change a user's password.

        Args:
            db (AsyncSession): The database session.
            user_id (UUID): User ID to change the password for.
            password_data (PasswordChange): Data containing the new password.

        Raises:
            NotFoundError: If the user is not found.
            InvalidPassword: If the current password is incorrect.
            PasswordMismatch: If the new passwords do not match.

        Returns:
            UserRead: The updated user with the new password.
        """
        user = await db.get(User, user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")

        # Verify current password
        if not verify_password(
            generate_password_hash(password_data.current_password), user.password_hash
        ):
            raise InvalidPasswordError()

        # Verify new passwords match
        if password_data.new_password != password_data.new_password_confirm:
            raise PasswordMismatchError()

        user.password_hash = generate_password_hash(password_data.new_password)
        await db.commit()
        return user
