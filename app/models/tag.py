from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING
from uuid import UUID, uuid4
from datetime import datetime

from app.models.product_tag import ProductTag
from app.utils.date_time_provider import get_utc_now

if TYPE_CHECKING:
    from app.models.product import Product


class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True, unique=True, nullable=False)
    slug: str = Field(index=True, unique=True, nullable=False)
    is_active: bool = Field(default=True, nullable=False)

    created_at: datetime = Field(default_factory=get_utc_now, nullable=False)
    updated_at: datetime = Field(default_factory=get_utc_now, nullable=False)

    # Relationship with products
    products: list["Product"] = Relationship(
        back_populates="tags",
        link_model=ProductTag,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
