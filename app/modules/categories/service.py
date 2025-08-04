from math import ceil
from typing import Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func
from uuid import UUID
from slugify import slugify


from app.models.category import Category
from app.exceptions import ConflictError, NotFoundError
from app.utils.paginate import PaginatedResponse
from .schemas import CategoryCreate, CategoryRead, CategoryUpdate


class CategoryService:
    @staticmethod
    async def list_categories(
        db: AsyncSession,
        page: int,
        page_size: int,
        is_active: Optional[bool] = None,
        name: Optional[str] = None,
    ) -> PaginatedResponse[CategoryRead]:
        """
        Retrieve a paginated list of categories with optional search functionality.
        Args:
            db (AsyncSession): The database session.
            page (int): The page number for pagination.
            page_size (int): The number of categories per page.
            is_active (Optional[bool]): Filter categories by active status.
            name (Optional[str]): A search term to filter categories by name.
        Returns:
            PaginatedResponse[CategoryRead]: A paginated response containing category data.
        """
        filters = CategoryService._build_filters(is_active, name)
        # Get total count based on filters
        count_stmt = select(func.count()).select_from(Category).where(*filters)
        total = (await db.exec(count_stmt)).one()

        # Get paginated categories
        stmt = (
            select(Category)
            .where(*filters)
            .order_by(Category.name)
            .limit(page_size)
            .offset((page - 1) * page_size)
        )

        categories = (await db.exec(stmt)).all()

        return PaginatedResponse[CategoryRead](
            total=total,
            page=page,
            size=page_size,
            pages=ceil(total / page_size) if total else 1,
            items=categories,
        )

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
            NotFoundError: If the category is not found.

        Returns:
            CategoryRead | CategoryReadDetail: The category details, either with or without children.
        """
        category = await db.get(Category, category_id)
        if not category:
            raise NotFoundError(f"Category with ID {category_id} not found")
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
            ConflictError: If a category with the same name already exists.

        Returns:
            CategoryRead: The created category details.
        """

        slug = slugify(category_data.name)
        existing_category = await CategoryService._get_category_by_slug(db, slug)
        if existing_category:
            raise ConflictError(
                f"Category with name {category_data.name} already exists."
            )

        category = Category(**category_data.model_dump(), slug=slug)
        db.add(category)
        await db.commit()
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
            NotFoundError: If the category is not found.
            ConflictError: If a category with the same name already exists.

        Returns:
            CategoryRead: The updated category details.
        """
        category = await db.get(Category, category_id)
        if not category:
            raise NotFoundError(f"Category with ID {category_id} not found")

        if update_data.name and update_data.name.lower() != category.name.lower():
            new_slug = slugify(update_data.name)
            existing_category = await CategoryService._get_category_by_slug(
                db, new_slug
            )

            if existing_category and existing_category.id != category_id:
                raise ConflictError(f"Category with slug {new_slug} already exists.")
            category.slug = new_slug

        # Apply updates
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(category, field, value)

        await db.commit()
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
            CategoryHasProducts: If the category has associated products.
        """
        category = await db.get(Category, category_id)

        if not category:
            raise NotFoundError(f"Category with ID {category_id} not found")

        await db.delete(category)
        await db.commit()

    @staticmethod
    async def _get_category_by_slug(db: AsyncSession, slug: str) -> Optional[Category]:
        """Get a category by its slug.
        Args:
            db (AsyncSession): The database session.
            slug (str): The slug of the category to retrieve.
        Returns:
            Optional[Category]: The category if found, otherwise None.
        """
        result = await db.exec(select(Category).where(Category.slug == slug))
        return result.first()

    @staticmethod
    def _build_filters(is_active: Optional[bool] = None, name: Optional[str] = None):
        """Build filters for category queries."""
        filters = []
        if is_active is not None:
            filters.append(Category.is_active == is_active)
        if name:
            filters.append(Category.name.ilike(f"%{name}%"))
        return filters
