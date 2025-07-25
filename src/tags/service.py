from datetime import datetime
from uuid import UUID
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.tag import Tag
from src.tags.schemas import TagCreate, TagRead, TagUpdate
from src.core.exceptions import TagAlreadyExists, TagNotFound
from slugify import slugify


class TagService:
    """Service class for managing tags in the system."""

    @staticmethod
    async def list_tags(db: AsyncSession) -> list[TagRead]:
        """
        Retrieve all tags from the database.

        Args:
            db (AsyncSession): The database session.

        Returns:
            list[TagRead]: A list of tags.
        """
        result = await db.exec(select(Tag))
        tags = result.all()
        return [TagRead(**tag.model_dump()) for tag in tags]

    @staticmethod
    async def get_tag(db: AsyncSession, tag_id: UUID) -> TagRead:
        """
        Retrieve a tag by its ID.

        Args:
            db (AsyncSession): The database session.
            tag_id (UUID): The tag's unique identifier.

        Returns:
            TagRead: The tag.

        Raises:
            TagNotFound: If the tag does not exist.
        """
        tag = await db.get(Tag, tag_id)
        if not tag:
            raise TagNotFound()
        return TagRead(**tag.model_dump())

    @staticmethod
    async def create_tag(db: AsyncSession, tag_data: TagCreate) -> TagRead:
        """
        Create a new tag with a unique slug.

        Args:
            db (AsyncSession): The database session.
            tag_data (TagCreate): The tag creation data.

        Returns:
            TagRead: The created tag.

        Raises:
            TagAlreadyExists: If the slug already exists.
        """
        slug = slugify(tag_data.name)
        exists = await db.exec(
            select(Tag).where(func.lower(Tag.slug) == func.lower(slug))
        )
        if exists.first():
            raise TagAlreadyExists()

        tag = Tag(name=tag_data.name, slug=slug)
        db.add(tag)
        await db.commit()
        await db.refresh(tag)
        return TagRead(**tag.model_dump())

    @staticmethod
    async def update_tag(db: AsyncSession, tag_id: UUID, tag_data: TagUpdate) -> TagRead:
        """
        Update an existing tag.

        Args:
            db (AsyncSession): The database session.
            tag_id (UUID): The tag's ID to update.
            tag_data (TagUpdate): New values for the tag.

        Returns:
            TagRead: The updated tag.

        Raises:
            TagNotFound: If the tag is not found.
            TagAlreadyExists: If the new slug conflicts with another tag.
        """
        tag = await db.get(Tag, tag_id)
        if not tag:
            raise TagNotFound()

        if tag_data.name:
            new_slug = slugify(tag_data.name)
            conflict = await db.exec(
                select(Tag)
                .where(func.lower(Tag.slug) == func.lower(new_slug))
                .where(Tag.id != tag_id)
            )
            if conflict.first():
                raise TagAlreadyExists()

            tag.name = tag_data.name
            tag.slug = new_slug
            tag.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(tag)
        return TagRead(**tag.model_dump())

    @staticmethod
    async def delete_tag(db: AsyncSession, tag_id: UUID) -> None:
        """
        Delete a tag by its ID.

        Args:
            db (AsyncSession): The database session.
            tag_id (UUID): The ID of the tag to delete.

        Raises:
            TagNotFound: If the tag does not exist.
        """
        tag = await db.get(Tag, tag_id)
        if not tag:
            raise TagNotFound()

        await db.delete(tag)
        await db.commit()
