from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import slugify


class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    slug: Optional[str] = Field(
        default=None, max_length=100, pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$"
    )
    description: Optional[str] = Field(None, max_length=500)

    @field_validator("slug")
    def set_slug(cls, v, values):
        return v or slugify.slugify(values["name"])


class CategoryCreate(CategoryBase):
    parent_id: Optional[UUID] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    slug: Optional[str] = Field(
        None, max_length=100, pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$"
    )
    description: Optional[str] = None
    parent_id: Optional[UUID] = None


class CategoryRead(CategoryBase):
    id: UUID
    parent_id: Optional[UUID]
    created_at: datetime


class CategoryReadDetail(CategoryRead):
    children: list["CategoryReadDetail"] = Field(default_factory=list)


# This is used to handle circular references in Pydantic models
CategoryReadDetail.model_rebuild()
