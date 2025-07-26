from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5, description="Rating must be between 1 and 5", lt=5)
    comment: Optional[str] = Field(
        default=None, max_length=500, description="Optional comment for the review"
    )


class ReviewRead(BaseModel):
    id: UUID
    rating: int
    comment: Optional[str]
    user_id: UUID
    product_id: UUID
    created_at: datetime
