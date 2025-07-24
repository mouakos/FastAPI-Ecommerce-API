from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    price: float = Field(..., ge=0)
    brand: str = Field(..., min_length=1, max_length=100)
    stock: int = Field(..., ge=0)
    sku: str = Field(..., min_length=1, max_length=50)
    category_id: UUID


class ProductCreate(ProductBase):
    pass


class ProductRead(ProductBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    brand: Optional[str] = Field(None, min_length=1, max_length=100)
    stock: Optional[int] = Field(None, ge=0)
    sku: Optional[str] = Field(None, min_length=1, max_length=50)
    category_id: Optional[UUID] = None
