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
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    slug: Optional[str] = Field(
        None, max_length=100, pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$"
    )
    description: Optional[str] = None


class CategoryRead(CategoryBase):
    id: UUID
    created_at: datetime
