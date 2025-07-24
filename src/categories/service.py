from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func
from sqlalchemy.orm import selectinload
from uuid import UUID

from src.categories.schemas import (
    CategoryCreate,
    CategoryRead,
    CategoryReadDetail,
    CategoryUpdate,
)
from src.models.category import Category
from src.core.exceptions import (
    CategoryAlreadyExists,
    CategoryHasChildren,
    CategoryNotFound,
    InvalidCategoryHierarchy,
    ParentCategoryNotFound,
)


class CategoryService:
    @staticmethod
    async def get_category_tree(
        db: AsyncSession,
        parent_id: UUID | None = None,
        max_depth: int = 1,
        current_depth: int = 0,
    ) -> list[CategoryReadDetail]:
        """
        Recursively fetch categories and their children up to a specified depth.
        Args:
            db (AsyncSession): The database session.
            parent_id (UUID | None, optional): The ID of the parent category. Defaults to None.
            max_depth (int, optional): The maximum depth to fetch. Defaults to 1.
            current_depth (int, optional): The current depth in the recursion. Defaults to 0.

        Returns:
            list[CategoryReadDetail]: A list of category details.
        """
        stmt = select(Category).where(Category.parent_id == parent_id)
        if current_depth < max_depth:
            stmt = stmt.options(selectinload(Category.children))
        result = await db.exec(stmt)
        categories = result.all()

        def build_tree(cat: Category, depth: int) -> CategoryReadDetail:
            children = (
                [build_tree(child, depth + 1) for child in getattr(cat, "children", [])]
                if depth < max_depth
                else []
            )
            return CategoryReadDetail(**cat.model_dump(), children=children)

        return [build_tree(cat, current_depth) for cat in categories]

    @staticmethod
    async def get_category(
        db: AsyncSession,
        category_id: UUID,
        include_children: bool = False,
    ) -> CategoryRead | CategoryReadDetail:
        """Get a category by its ID.

        Args:
            db (AsyncSession): The database session.
            category_id (UUID): The ID of the category to retrieve.
            include_children (bool, optional): Whether to include child categories. Defaults to False.

        Raises:
            CategoryNotFound: If the category is not found.

        Returns:
            CategoryRead | CategoryReadDetail: The category details, either with or without children.
        """
        if not include_children:
            stmt = select(Category).where(Category.id == category_id)
            result = await db.exec(stmt)
            category = result.first()
            if not category:
                raise CategoryNotFound()
            return CategoryRead(**category.model_dump())

        # Eagerly load all categories
        stmt = select(Category)
        result = await db.exec(stmt)
        all_categories = result.all()
        category_map = {cat.id: cat for cat in all_categories}
        children_map = {}
        for cat in all_categories:
            children_map.setdefault(cat.parent_id, []).append(cat)

        def build_tree(cat_id):
            cat = category_map[cat_id]
            children = [build_tree(child.id) for child in children_map.get(cat_id, [])]
            return CategoryReadDetail(**cat.model_dump(), children=children)

        if category_id not in category_map:
            raise CategoryNotFound()
        return build_tree(category_id)

    @staticmethod
    async def create_category(
        db: AsyncSession, category_data: CategoryCreate
    ) -> CategoryRead:
        """Create a new category.

        Args:
            db (AsyncSession): The database session.
            category_data (CategoryCreate): The category data to create.

        Raises:
            ParentCategoryNotFound: If the parent category is not found.
            CategoryAlreadyExists: If a category with the same name or slug already exists.

        Returns:
            CategoryRead: The created category details.
        """
        async with db.begin():
            # Validate parent exists
            if category_data.parent_id:
                parent = await db.get(Category, category_data.parent_id)
                if not parent:
                    raise ParentCategoryNotFound()

            # Check for duplicate slug/name
            exists = await db.exec(
                select(Category).where(
                    (func.lower(Category.slug) == func.lower(category_data.slug))
                    | (func.lower(Category.name) == func.lower(category_data.name))
                )
            )
            if exists.first():
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
            InvalidCategoryHierarchy: If the category hierarchy is invalid.
            CategoryAlreadyExists: If a category with the same name or slug already exists.

        Returns:
            CategoryRead: The updated category details.
        """
        async with db.begin():
            category = await db.get(Category, category_id)
            if not category:
                raise CategoryNotFound()

            # Prevent circular references
            if update_data.parent_id:
                if update_data.parent_id == category_id:
                    raise InvalidCategoryHierarchy()

                # Check for ancestor chain
                current_parent = update_data.parent_id
                while current_parent:
                    if current_parent == category_id:
                        raise InvalidCategoryHierarchy()
                    parent = await db.get(Category, current_parent)
                    current_parent = parent.parent_id if parent else None

            exists = await db.exec(
                select(Category).where(
                    (
                        (func.lower(Category.name) == func.lower(update_data.name))
                        | (func.lower(Category.slug) == func.lower(update_data.slug))
                    )
                    & (Category.id != category_id)
                )
            )
            if exists.first():
                raise CategoryAlreadyExists()

            # Apply updates
            for field, value in update_data.model_dump(exclude_unset=True).items():
                setattr(category, field, value)

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
            CategoryHasChildren: If the category has child categories.
        """
        async with db.begin():
            category = await db.get(Category, category_id)
            if not category:
                raise CategoryNotFound()

            # Check for children
            count_result = await db.exec(
                select(func.count(Category.id)).where(Category.parent_id == category_id)
            )
            child_count = count_result.first()
            if child_count > 0:
                raise CategoryHasChildren()
            await db.delete(category)
