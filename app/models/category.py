from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from app.models.product import Product


class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True, nullable=False, unique=True)
    slug: str = Field(index=True, nullable=False, unique=True)
    description: Optional[str] = Field(default=None, nullable=True)
    is_active: bool = Field(default=True, nullable=False)

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship with products - one-to-many
    products: list["Product"] = Relationship(
        back_populates="category", sa_relationship_kwargs={"lazy": "selectin"}
    )
