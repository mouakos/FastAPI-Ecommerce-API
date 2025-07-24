from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from src.models.category import Category


class Product(SQLModel, table=True):
    __tablename__ = "products"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True, nullable=False)
    slug: str = Field(index=True, nullable=False, unique=True)
    description: Optional[str] = Field(default=None)
    price: float = Field(default=0.0, nullable=False)
    brand: str = Field(default=None, nullable=False)
    stock: int = Field(default=0, nullable=False)
    sku: str = Field(index=True, unique=True, nullable=False)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship with category
    category_id: UUID = Field(default=None, foreign_key="categories.id", nullable=False)
    category: Optional["Category"] = Relationship(back_populates="products")
