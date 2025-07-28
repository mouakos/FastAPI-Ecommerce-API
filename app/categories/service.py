from datetime import datetime
from math import ceil
from typing import Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func
from uuid import UUID
from slugify import slugify

from app.categories.schemas import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
)
from app.models.category import Category
from app.core.exceptions import (
    CategoryAlreadyExists,
    CategoryHasProducts,
    CategoryNotFound,
)
from app.utils.paginate import PaginatedResponse


class CategoryService:
    @staticmethod
    async def list_categories(
        db_session: AsyncSession,
        page: int,
        page_size: int,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> PaginatedResponse[CategoryRead]:
        """
        Retrieve a paginated list of categories with optional search functionality.
        Args:
            db_session (AsyncSession): The database session.
            page (int): The page number for pagination.
            page_size (int): The number of categories per page.
            is_active (Optional[bool]): Filter categories by active status.
            search (Optional[str]): A search term to filter categories by name.
        Returns:
            PaginatedResponse[CategoryRead]: A paginated response containing category data.
        """
        # Get total count (without limit/offset)
        count_stmt = (
            select(func.count())
            .select_from(Category)
            .where(
                (Category.name.ilike(f"%{search}%")) if search else True,
                (Category.is_active == is_active) if is_active is not None else True,
            )
        )
        total = (await db_session.exec(count_stmt)).one()

        # Get paginated categories
        result = await db_session.exec(
            select(Category)
            .where(
                (Category.name.ilike(f"%{search}%")) if search else True,
                (Category.is_active == is_active) if is_active is not None else True,
            )
            .order_by(Category.created_at.desc())
            .limit(page_size)
            .offset((page - 1) * page_size)
        )
        categories = result.all()

        return PaginatedResponse[CategoryRead](
            total=total,
            page=page,
            size=page_size,
            pages=ceil(total / page_size) if total else 1,
            items=[CategoryRead(**category.model_dump()) for category in categories],
        )

    @staticmethod
    async def get_category(
        db_session: AsyncSession,
        category_id: UUID,
    ) -> Category:
        """Get a category by its ID.

        Args:
            db_session (AsyncSession): The database session.
            category_id (UUID): The ID of the category to retrieve.

        Raises:
            CategoryNotFound: If the category is not found.

        Returns:
            CategoryRead | CategoryReadDetail: The category details, either with or without children.
        """
        stmt = select(Category).where(Category.id == category_id)
        result = await db_session.exec(stmt)
        category = result.first()
        if not category:
            raise CategoryNotFound()
        return category

    @staticmethod
    async def create_category(
        db_session: AsyncSession, category_data: CategoryCreate
    ) -> CategoryRead:
        """Create a new category.

        Args:
            db_session (AsyncSession): The database session.
            category_data (CategoryCreate): The category data to create.

        Raises:
            CategoryAlreadyExists: If a category with the same name already exists.

        Returns:
            CategoryRead: The created category details.
        """

        slug = slugify(category_data.name)
        exists = await db_session.exec(
            select(Category).where(func.lower(Category.slug) == func.lower(slug))
        )
        if exists.first():
            raise CategoryAlreadyExists()

        category = Category(**category_data.model_dump(), slug=slug)
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)
        return CategoryRead(**category.model_dump())

    @staticmethod
    async def update_category(
        db_session: AsyncSession, category_id: UUID, update_data: CategoryUpdate
    ) -> CategoryRead:
        """Update an existing category.

        Args:
            db_session (AsyncSession): The database session.
            category_id (UUID): The ID of the category to update.
            update_data (CategoryUpdate): The updated category data.

        Raises:
            CategoryNotFound: If the category is not found.
            CategoryAlreadyExists: If a category with the same name already exists.

        Returns:
            CategoryRead: The updated category details.
        """
        category = await db_session.get(Category, category_id)
        if not category:
            raise CategoryNotFound()

        if update_data.name and update_data.name.lower() != category.name.lower():
            new_slug = slugify(update_data.name)
            conflict = await db_session.exec(
                select(Category)
                .where(func.lower(Category.slug) == func.lower(new_slug))
                .where(Category.id != category_id)
            )
            if conflict.first():
                raise CategoryAlreadyExists()
            category.slug = new_slug

        # Apply updates
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(category, field, value)

        # TODO - Check if fields are actually changed
        category.updated_at = datetime.utcnow()
        await db_session.commit()
        await db_session.refresh(category)
        return CategoryRead(**category.model_dump())

    @staticmethod
    async def delete_category(db_session: AsyncSession, category_id: UUID) -> None:
        """Delete a category by its ID.
        Args:
            db_session (AsyncSession): The database session.
            category_id (UUID): The ID of the category to delete.
        Raises:
            CategoryNotFound: If the category is not found.
            CategoryHasProducts: If the category has associated products.
        """
        category = await db_session.get(Category, category_id)

        if not category:
            raise CategoryNotFound()

        if category.products:
            raise CategoryHasProducts()

        await db_session.delete(category)
        await db_session.commit()
