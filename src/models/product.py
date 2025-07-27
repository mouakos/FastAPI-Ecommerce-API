from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime
from uuid import UUID, uuid4

from src.models.product_tag import ProductTag

if TYPE_CHECKING:
    from src.models.category import Category
    from src.models.tag import Tag
    from src.models.review import Review
    from src.models.cart_item import CartItem


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
    rating: float = Field(default=0.0, nullable=False)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship with category - many-to-one
    category_id: UUID = Field(default=None, foreign_key="categories.id", nullable=False)
    category: "Category" = Relationship(
        back_populates="products", sa_relationship_kwargs={"lazy": "selectin"}
    )

    # Relationship with tags - many-to-many
    tags: list["Tag"] = Relationship(
        back_populates="products",
        link_model=ProductTag,
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    # Relationship with reviews - one-to-many
    reviews: list["Review"] = Relationship(
        back_populates="product", sa_relationship_kwargs={"lazy": "selectin"}
    )

    # Realationship with cart items - one-to-many
    cart_items: list["CartItem"] = Relationship(
        back_populates="product", sa_relationship_kwargs={"lazy": "selectin"}
    )
