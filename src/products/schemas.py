from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

from src.categories.schemas import CategoryRead
from src.reviews.schemas import ReviewRead
from src.tags.schemas import TagRead


class ProductBase(BaseModel):
    name: str = Field(
        ..., min_length=1, max_length=100, description="Name of the product"
    )
    description: Optional[str] = Field(None, description="Description of the product")
    price: float = Field(..., ge=0, description="Price of the product")
    brand: str = Field(
        ..., min_length=1, max_length=100, description="Brand of the product"
    )
    stock: int = Field(..., ge=0, description="Stock quantity of the product")
    sku: str = Field(..., min_length=1, max_length=50, description="SKU of the product")


class ProductCreate(ProductBase):
    category_id: UUID = Field(
        ..., description="ID of the category this product belongs to"
    )
    tag_ids: Optional[list[UUID]] = Field(
        default_factory=list, description="List of tag IDs associated with the product"
    )


class ProductRead(ProductCreate):
    id: UUID = Field(..., description="Unique identifier of the product")
    is_active: bool = Field(
        default=True, description="Indicates if the product is active"
    )
    slug: str = Field(..., description="Slug of the product")
    created_at: datetime = Field(..., description="Creation timestamp of the product")
    updated_at: datetime = Field(
        ..., description="Last update timestamp of the product"
    )


class ProductReadDetail(ProductBase):
    id: UUID = Field(..., description="Unique identifier of the product")
    slug: str = Field(..., description="Slug of the product")
    is_active: bool = Field(
        default=True, description="Indicates if the product is active"
    )
    created_at: datetime = Field(..., description="Creation timestamp of the product")
    updated_at: datetime = Field(
        ..., description="Last update timestamp of the product"
    )
    category: CategoryRead = Field(..., description="Category of the product")
    tags: list[TagRead] = Field(
        default_factory=list, description="List of tags associated with the product"
    )
    reviews: list[ReviewRead] = Field(
        default_factory=list, description="List of reviews for the product"
    )


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Name of the product"
    )
    is_active: Optional[bool] = Field(
        None, description="Indicates if the product is active"
    )
    sku: Optional[str] = Field(
        None, min_length=1, max_length=50, description="SKU of the product"
    )
    description: Optional[str] = Field(None, description="Description of the product")
    price: Optional[float] = Field(None, ge=0, description="Price of the product")
    brand: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Brand of the product"
    )
    stock: Optional[int] = Field(
        None, ge=0, description="Stock quantity of the product"
    )
    category_id: Optional[UUID] = Field(
        None, description="ID of the category this product belongs to"
    )
    tag_ids: Optional[list[UUID]] = Field(
        default_factory=list, description="List of tag IDs associated with the product"
    )
