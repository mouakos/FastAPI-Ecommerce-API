from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .product import Product


class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False, unique=True)
    slug: str = Field(index=True, nullable=False, unique=True)
    description: Optional[str] = Field(default=None, nullable=True)
    is_active: bool = Field(default=True, nullable=False)

    # Relationship with products - one-to-many
    products: list["Product"] = Relationship(
        back_populates="category", sa_relationship_kwargs={"lazy": "selectin"}
    )
