from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from .product_tag import ProductTag

if TYPE_CHECKING:
    from app.models.product import Product


class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True, unique=True, nullable=False)
    slug: str = Field(index=True, unique=True, nullable=False)
    is_active: bool = Field(default=True, nullable=False)

    # Relationship with products
    products: list["Product"] = Relationship(
        back_populates="tags",
        link_model=ProductTag,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
