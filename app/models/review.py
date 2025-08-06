from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.user import User


class Review(SQLModel, table=True):
    __tablename__ = "reviews"

    id: int | None = Field(default=None, primary_key=True)
    rating: int = Field(ge=1, le=5, nullable=False)
    comment: Optional[str] = Field(default=None)
    is_published: bool = Field(default=False, nullable=False)

    # Relationship with product - many-to-one
    product_id: int = Field(foreign_key="products.id", nullable=False)
    product: Optional["Product"] = Relationship(back_populates="reviews")

    # Relationship with user - many-to-one
    user_id: int = Field(foreign_key="users.id", nullable=False)
    user: Optional["User"] = Relationship(back_populates="reviews")
