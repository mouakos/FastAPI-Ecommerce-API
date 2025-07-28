from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    rating: int = Field(description="Rating must be between 1 and 5", ge=1, le=5)
    comment: Optional[str] = Field(
        default=None, max_length=500, description="Optional comment for the review"
    )


class ReviewRead(BaseModel):
    id: UUID = Field(..., description="Unique identifier for the review")
    rating: int = Field(..., description="Rating given by the user")
    comment: Optional[str] = Field(
        default=None, description="Comment provided by the user"
    )
    user_id: UUID = Field(..., description="ID of the user who wrote the review")
    product_id: UUID = Field(..., description="ID of the product being reviewed")
    created_at: datetime = Field(
        ..., description="Timestamp when the review was created"
    )
    updated_at: datetime = Field(
        ..., description="Timestamp when the review was last updated"
    )


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(
        ge=1, le=5, description="Rating must be between 1 and 5"
    )
    comment: Optional[str] = Field(
        default=None, max_length=500, description="Optional comment for the review"
    )
