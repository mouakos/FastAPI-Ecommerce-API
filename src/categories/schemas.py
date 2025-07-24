from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional
import slugify


class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=500)

  


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None


class CategoryRead(CategoryBase):
    id: UUID
    created_at: datetime
