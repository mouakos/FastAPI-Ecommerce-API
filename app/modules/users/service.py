from math import ceil
from typing import Optional
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func

from app.exceptions import BadRequestError, NotFoundError
from app.utils.security import get_password_hash, verify_password
from app.models.user import User
from app.utils.paginate import PaginatedResponse
from .schemas import (
    PasswordUpdate,
    UserRead,
    UserReadDetail,
    UserUpdate,
)


class UserService:
    @staticmethod
    async def get_all_users(
        db: AsyncSession,
        page: int,
        page_size: int,
        role: Optional[str],
        is_active: Optional[bool],
        email: Optional[str],
    ) -> PaginatedResponse[UserRead]:
        """Retrieve all users with pagination and optional filters.

        Args:
            db (AsyncSession): The database session.
            page (int): Page number for pagination.
            page_size (int): Number of users per page.
            role (Optional[UserRole]): Filter by user role.
            email (Optional[str]): Search term to filter users by email.

        Returns:
            PaginatedResponse[UserRead]: A paginated response containing user data.
        """
        filters = UserService._build_user_filters(role, is_active, email)
        stmt_count = select(func.count()).select_from(User).where(*filters)
        total = (await db.exec(stmt_count)).one()

        stmt = (
            select(User)
            .where(*filters)
            .order_by(User.fistname)
            .limit(page_size)
            .offset((page - 1) * page_size)
        )

        result = await db.exec(stmt)
        users = result.all()
        return PaginatedResponse[UserRead](
            total=total,
            page=page,
            size=page_size,
            pages=ceil(total / page_size) if total else 1,
            items=users,
        )

    @staticmethod
    async def get_user(db: AsyncSession, user_id: UUID) -> UserReadDetail:
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
            get_password_hash(password_data.current_password), user.password_hash
        ):
            raise BadRequestError("Invalid password.")

        # Verify new passwords match
        if password_data.new_password != password_data.new_password_confirm:
            raise BadRequestError("New passwords do not match.")

        user.password_hash = get_password_hash(password_data.new_password)
        await db.commit()
        return user

    @staticmethod
    def _build_user_filters(
        role: Optional[str], is_active: Optional[bool], email: Optional[str]
    ):
        filters = []
        if role:
            filters.append(User.role == role)
        if is_active is not None:
            filters.append(User.is_active == is_active)
        if email:
            filters.append(User.email.ilike(f"%{email}%"))
        return filters
