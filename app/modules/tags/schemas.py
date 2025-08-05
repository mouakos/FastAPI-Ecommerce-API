from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class TagBase(BaseModel):
    name: str = Field(..., max_length=255, description="Name of the tag")


class TagAdd(TagBase):
    tags: list[UUID] = Field(
        ..., description="List of tag IDs to be added to the product"
    )


class TagCreate(TagBase):
    pass


class TagUpdate(TagBase):
    name: Optional[str] = Field(None, max_length=255, description="Name of the tag")


class TagRead(TagBase):
    id: UUID = Field(..., description="Unique identifier of the tag")
    slug: str = Field(..., description="Slug for the tag, used in URLs")
