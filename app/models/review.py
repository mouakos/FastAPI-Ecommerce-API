from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.user import User


class Review(SQLModel, table=True):
    __tablename__ = "reviews"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    rating: int = Field(ge=1, le=5, nullable=False)
    comment: Optional[str] = Field(default=None)
    is_published: bool = Field(default=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship with product - many-to-one
    product_id: UUID = Field(foreign_key="products.id", nullable=False)
    product: "Product" = Relationship(back_populates="reviews")

    # Relationship with user - many-to-one
    user_id: UUID = Field(foreign_key="users.id", nullable=False)
    user: "User" = Relationship(back_populates="reviews")
