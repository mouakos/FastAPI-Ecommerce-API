from datetime import datetime
from math import ceil
from typing import Optional
from uuid import UUID
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.tag import Tag
from src.tags.schemas import TagCreate, TagRead, TagUpdate
from src.core.exceptions import TagAlreadyExists, TagNotFound
from slugify import slugify

from src.utils.paginate import PaginatedResponse


class TagService:
    """Service class for managing tags in the system."""

    @staticmethod
    async def list_tags(
        db_session: AsyncSession, page: int, page_size: int, search: Optional[str]
    ) -> PaginatedResponse[TagRead]:
        """
        Retrieve a paginated list of tags with optional search functionality.

        Args:
            db_session (AsyncSession): The database session.
            page (int): The page number for pagination.
            page_size (int): The number of tags per page.
            search (Optional[str]): A search term to filter tags by name.

        Returns:
            PaginatedResponse[TagRead]: A paginated response containing the tags.
        """
        # Get total count (without limit/offset)
        count_stmt = (
            select(func.count())
            .select_from(Tag)
            .where(
                (Tag.name.ilike(f"%{search}%")) if search else True,
            )
        )
        total = (await db_session.exec(count_stmt)).one()

        # Get paginated tags
        result = await db_session.exec(
            select(Tag)
            .where(
                (Tag.name.ilike(f"%{search}%")) if search else True,
            )
            .order_by(Tag.created_at.desc())
            .limit(page_size)
            .offset((page - 1) * page_size)
        )
        tags = result.all()

        return PaginatedResponse[TagRead](
            total=total,
            page=page,
            size=page_size,
            pages=ceil(total / page_size) if total else 1,
            items=[TagRead(**tag.model_dump()) for tag in tags],
        )

    @staticmethod
    async def get_tag(db_session: AsyncSession, tag_id: UUID) -> TagRead:
        """
        Retrieve a tag by its ID.

        Args:
            db_session (AsyncSession): The database session.
            tag_id (UUID): The tag's unique identifier.

        Returns:
            TagRead: The tag.

        Raises:
            TagNotFound: If the tag does not exist.
        """
        tag = await db_session.get(Tag, tag_id)
        if not tag:
            raise TagNotFound()
        return TagRead(**tag.model_dump())

    @staticmethod
    async def create_tag(db_session: AsyncSession, tag_data: TagCreate) -> TagRead:
        """
        Create a new tag with a unique slug.

        Args:
            db_session (AsyncSession): The database session.
            tag_data (TagCreate): The tag creation data.

        Returns:
            TagRead: The created tag.

        Raises:
            TagAlreadyExists: If the slug already exists.
        """
        slug = slugify(tag_data.name)
        exists = await db_session.exec(
            select(Tag).where(func.lower(Tag.slug) == func.lower(slug))
        )
        if exists.first():
            raise TagAlreadyExists()

        tag = Tag(name=tag_data.name, slug=slug)
        db_session.add(tag)
        await db_session.commit()
        await db_session.refresh(tag)
        return TagRead(**tag.model_dump())

    @staticmethod
    async def update_tag(
        db_session: AsyncSession, tag_id: UUID, tag_data: TagUpdate
    ) -> TagRead:
        """
        Update an existing tag.

        Args:
            db_session (AsyncSession): The database session.
            tag_id (UUID): The tag's ID to update.
            tag_data (TagUpdate): New values for the tag.

        Returns:
            TagRead: The updated tag.

        Raises:
            TagNotFound: If the tag is not found.
            TagAlreadyExists: If the new slug conflicts with another tag.
        """

        tag = await db_session.get(Tag, tag_id)
        if not tag:
            raise TagNotFound()

        if tag_data.name and tag_data.name.lower() != tag.name.lower():
            new_slug = slugify(tag_data.name)
            conflict = await db_session.exec(
                select(Tag)
                .where(func.lower(Tag.slug) == func.lower(new_slug))
                .where(Tag.id != tag_id)
            )
            if conflict.first():
                raise TagAlreadyExists()

            tag.name = tag_data.name
            tag.slug = new_slug
            tag.updated_at = datetime.utcnow()
        await db_session.commit()
        await db_session.refresh(tag)
        return TagRead(**tag.model_dump())

    @staticmethod
    async def delete_tag(db_session: AsyncSession, tag_id: UUID) -> None:
        """
        Delete a tag by its ID.

        Args:
            db_session (AsyncSession): The database session.
            tag_id (UUID): The ID of the tag to delete.

        Raises:
            TagNotFound: If the tag does not exist.
        """

        tag = await db_session.get(Tag, tag_id)
        if not tag:
            raise TagNotFound()

        await db_session.delete(tag)
        await db_session.commit()
