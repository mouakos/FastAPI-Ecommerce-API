from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional


class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100, description="Name of the category")
    description: Optional[str] = Field(
        None, max_length=500, description="Description of the category"
    )


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(
        None, max_length=100, description="Name of the category"
    )
    description: Optional[str] = Field(
        None, max_length=500, description="Description of the category"
    )
    is_active: Optional[bool] = Field(
        None, description="Indicates if the category is active"
    )


class CategoryRead(CategoryBase):
    id: UUID = Field(..., description="Unique identifier of the category")
    slug: str = Field(..., description="Slug of the category for URL usage")
    is_active: bool = Field(..., description="Indicates if the category is active")
