from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class TagBase(BaseModel):
    name: str = Field(..., max_length=255, description="Name of the tag")


class TagCreate(TagBase):
    pass


class TagUpdate(TagBase):
    name: Optional[str] = Field(None, max_length=255, description="Name of the tag")
    is_active: Optional[bool] = Field(
        None, description="Indicates if the tag is active or not"
    )


class TagRead(TagBase):
    id: UUID = Field(..., description="Unique identifier of the tag")
    slug: str = Field(..., description="Slug for the tag, used in URLs")
    is_active: bool = Field(..., description="Indicates if the tag is active or not")
    created_at: datetime = Field(..., description="Timestamp when the tag was created")
    updated_at: datetime = Field(
        ..., description="Timestamp when the tag was last updated"
    )
