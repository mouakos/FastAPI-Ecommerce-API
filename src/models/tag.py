from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING
from uuid import UUID, uuid4
from datetime import datetime

from src.models.product_tag import ProductTag

if TYPE_CHECKING:
    from src.models.product import Product


class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True, unique=True, nullable=False)
    slug: str = Field(index=True, unique=True, nullable=False)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship with products
    products: list["Product"] = Relationship(
        back_populates="tags", link_model=ProductTag
    )
