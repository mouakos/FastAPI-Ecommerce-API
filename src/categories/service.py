from datetime import datetime
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi_pagination.ext.sqlmodel import paginate as sqlmodel_paginate
from fastapi_pagination import Page
from sqlmodel import select, func
from uuid import UUID

from src.categories.schemas import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
)
from src.models.category import Category
from src.core.exceptions import CategoryAlreadyExists, CategoryNotFound


class CategoryService:
    @staticmethod
    async def get_category_tree(db: AsyncSession, search: str = "") -> Page[Category]:
        """
        Recursively fetch categories and their children up to a specified depth.
        Args:
            db (AsyncSession): The database session.
            search (str): Search term to filter categories by name.

        Returns:
            list[CategoryRead]: A list of categories.
        """
        stmt = (
            select(Category)
            .where(func.lower(Category.name).like(f"%{search.lower()}%"))
            .order_by(Category.name)
        )

        return await sqlmodel_paginate(db, stmt)

    @staticmethod
    async def get_category(
        db: AsyncSession,
        category_id: UUID,
    ) -> Category:
        """Get a category by its ID.

        Args:
            db (AsyncSession): The database session.
            category_id (UUID): The ID of the category to retrieve.

        Raises:
            CategoryNotFound: If the category is not found.

        Returns:
            CategoryRead | CategoryReadDetail: The category details, either with or without children.
        """
        stmt = select(Category).where(Category.id == category_id)
        result = await db.exec(stmt)
        category = result.first()
        if not category:
            raise CategoryNotFound()
        return category

    @staticmethod
    async def create_category(
        db: AsyncSession, category_data: CategoryCreate
    ) -> CategoryRead:
        """Create a new category.

        Args:
            db (AsyncSession): The database session.
            category_data (CategoryCreate): The category data to create.

        Raises:
            CategoryAlreadyExists: If a category with the same name already exists.

        Returns:
            CategoryRead: The created category details.
        """
        async with db.begin():
            if await CategoryService._get_category_by_name(db, category_data.name):
                raise CategoryAlreadyExists()

            category = Category(**category_data.model_dump())
            db.add(category)
        await db.refresh(category)
        return CategoryRead(**category.model_dump())

    @staticmethod
    async def update_category(
        db: AsyncSession, category_id: UUID, update_data: CategoryUpdate
    ) -> CategoryRead:
        """Update an existing category.

        Args:
            db (AsyncSession): The database session.
            category_id (UUID): The ID of the category to update.
            update_data (CategoryUpdate): The updated category data.

        Raises:
            CategoryNotFound: If the category is not found.
            CategoryAlreadyExists: If a category with the same name already exists.

        Returns:
            CategoryRead: The updated category details.
        """
        async with db.begin():
            category = await db.get(Category, category_id)
            if not category:
                raise CategoryNotFound()

            if update_data.name and await CategoryService._get_category_by_name(
                db, update_data.name
            ):
                raise CategoryAlreadyExists()

            # Apply updates
            for field, value in update_data.model_dump(exclude_unset=True).items():
                setattr(category, field, value)
            category.updated_at = datetime.utcnow()

        await db.refresh(category)
        return CategoryRead(**category.model_dump())

    @staticmethod
    async def delete_category(db: AsyncSession, category_id: UUID) -> None:
        """Delete a category by its ID.
        Args:
            db (AsyncSession): The database session.
            category_id (UUID): The ID of the category to delete.
        Raises:
            CategoryNotFound: If the category is not found.
        """
        async with db.begin():
            category = await db.get(Category, category_id)
            if not category:
                raise CategoryNotFound()
            await db.delete(category)

    @staticmethod
    async def _get_category_by_name(db: AsyncSession, name: str) -> Category | None:
        """Get a category by its name.

        Args:
            db (AsyncSession): The database session.
            name (str): The name of the category.

        Returns:
            Category | None: The category if found, None otherwise.
        """
        return (
            await db.exec(
                select(Category).where(func.lower(Category.name) == func.lower(name))
            )
        ).first()
