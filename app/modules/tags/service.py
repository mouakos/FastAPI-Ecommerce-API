from math import ceil
from typing import Optional
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func
from slugify import slugify

from app.exceptions import ConflictError, NotFoundError
from app.models.tag import Tag
from app.modules.products.service import ProductService
from app.utils.paginate import PaginatedResponse
from .schemas import TagAdd, TagCreate, TagRead, TagUpdate


class TagService:
    """Service class for managing tags in the system."""

    @staticmethod
    async def list_tags(
        db: AsyncSession,
        page: int,
        page_size: int,
        name: Optional[str],
    ) -> PaginatedResponse[TagRead]:
        """
        Retrieve a paginated list of tags with optional search functionality.

        Args:
            db (AsyncSession): The database session.
            page (int): The page number for pagination.
            page_size (int): The number of tags per page.
            name (Optional[str]): A search term to filter tags by name.

        Returns:
            PaginatedResponse[TagRead]: A paginated response containing the tags.
        """
        filters = TagService._build_tag_filter(name)
        stmt_count = select(func.count()).select_from(Tag).where(*filters)
        total = (await db.exec(stmt_count)).one()
        stmt = (
            select(Tag)
            .where(*filters)
            .order_by(Tag.name)
            .limit(page_size)
            .offset((page - 1) * page_size)
        )

        result = await db.exec(stmt)
        tags = result.all()

        return PaginatedResponse[Tag](
            total=total,
            page=page,
            size=page_size,
            pages=ceil(total / page_size) if total else 1,
            items=tags,
        )

    @staticmethod
    async def get_tag(db: AsyncSession, tag_id: UUID) -> TagRead:
        """
        Retrieve a tag by its ID.

        Args:
            db (AsyncSession): The database session.
            tag_id (UUID): The ID of the tag to retrieve.

        Raises:
            NotFoundError: If the tag is not found.

        Returns:
            TagReadDetail: The retrieved tag.
        """
        tag = await db.get(Tag, tag_id)
        if not tag:
            raise NotFoundError(f"Tag with ID {tag_id} not found")
        return tag

    @staticmethod
    async def create_tag(db: AsyncSession, data: TagCreate) -> TagRead:
        """Create a new tag.

        Args:
            db (AsyncSession): The database session.
            data (TagCreate): The data for the new tag.

        Raises:
            ResourceAlreadyExistsError: If a tag with the same name already exists.

        Returns:
            TagRead: The created tag.
        """
        slug = slugify(data.name)
        existing_tag = (await db.exec(select(Tag).where(Tag.slug == slug))).first()
        if existing_tag:
            raise ConflictError(f"Tag with name '{data.name}' already exists.")
        tag = Tag(name=data.name, slug=slug)

        await db.add(tag)
        await db.commit()
        return tag

    @staticmethod
    async def update_tag(db: AsyncSession, tag_id: UUID, data: TagUpdate) -> TagRead:
        """Update an existing tag.

        Args:
            db (AsyncSession): The database session.
            tag_id (UUID): The ID of the tag to update.
            data (TagUpdate): The updated tag data.

        Raises:
            NotFoundError: If the tag is not found.
            ConflictError: If a tag with the same name already exists.

        Returns:
            TagRead: The updated tag.
        """
        tag = await db.get(Tag, tag_id)
        if not tag:
            raise NotFoundError(f"Tag with ID {tag_id} not found")

        if data.name and data.name.lower() != tag.name.lower():
            new_slug = slugify(data.name)
            existing_tag = (
                await db.exec(select(Tag).where(Tag.slug == new_slug))
            ).first()
            if existing_tag and existing_tag.id != tag_id:
                raise ConflictError(f"Tag with name '{data.name}' already exists.")
            tag.name = data.name
            tag.slug = new_slug

        for item, value in data.model_dump(
            exclude_unset=True, exclude={"name", "slug"}
        ).items():
            setattr(tag, item, value)

        await db.commit()
        return tag

    @staticmethod
    async def delete_tag(db: AsyncSession, tag_id: UUID) -> None:
        """
        Delete a tag by its ID.

        Args:
            db (AsyncSession): The database session.
            tag_id (UUID): The ID of the tag to delete.

        Raises:
            NotFoundError: If the tag does not exist.
        """

        tag = await db.get(Tag, tag_id)
        if not tag:
            raise NotFoundError(f"Tag with ID {tag_id} not found")
        await db.delete(tag)
        await db.commit()

    @staticmethod
    def _build_tag_filter(name: Optional[str], is_active: Optional[bool]) -> list:
        """Build filter conditions for tag queries."""
        filters = []
        if name:
            filters.append(Tag.name.ilike(f"%{name}%"))
        return filters

    @staticmethod
    async def add_tags_to_product(
        db: AsyncSession, tags: TagAdd, product_id: UUID
    ) -> None:
        """
        Assign tags to a product.

        Args:
            db (AsyncSession): The database session.
            tags (TagAdd): The tags to assign to the product.
            product_id (UUID): The ID of the product.

        Raises:
            NotFoundError: If the product or any tag does not exist.
        """
        product = await ProductService.get_product(db, product_id)

        for tag_id in tags.tags:
            tag = await db.get(Tag, tag_id)
            if not tag:
                raise NotFoundError(f"Tag with ID {tag_id} not found")
            if tag not in product.tags:
                product.tags.append(tag)

        await db.commit()

    @staticmethod
    async def remove_tag_from_product(
        db: AsyncSession, tag_id: UUID, product_id: UUID
    ) -> None:
        """
        Remove a tag from a product.

        Args:
            db (AsyncSession): The database session.
            tag_id (UUID): The ID of the tag to remove.
            product_id (UUID): The ID of the product.

        Raises:
            NotFoundError: If the product or tag does not exist.
        """
        product = await ProductService.get_product(db, product_id)
        tag = await db.get(Tag, tag_id)
        if not tag:
            raise NotFoundError(f"Tag with ID {tag_id} not found")

        if tag in product.tags:
            product.tags.remove(tag)
            await db.commit()
