from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

from src.categories.schemas import CategoryRead
from src.reviews.schemas import ReviewRead
from src.tags.schemas import TagRead


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    price: float = Field(..., ge=0)
    brand: str = Field(..., min_length=1, max_length=100)
    stock: int = Field(..., ge=0)
    sku: str = Field(..., min_length=1, max_length=50)


class ProductCreate(ProductBase):
    category_id: UUID
    tag_ids: Optional[list[UUID]] = Field(default_factory=list)


class ProductRead(ProductCreate):
    id: UUID
    slug: str
    created_at: datetime
    updated_at: datetime


class ProductReadDetail(ProductBase):
    id: UUID
    slug: str
    created_at: datetime
    updated_at: datetime
    category: CategoryRead = None
    tags: list[TagRead] = Field(default_factory=list)
    reviews: list[ReviewRead] = Field(default_factory=list)


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    sku: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    brand: Optional[str] = Field(None, min_length=1, max_length=100)
    stock: Optional[int] = Field(None, ge=0)
    category_id: Optional[UUID] = None
    tag_ids: Optional[list[UUID]] = None
