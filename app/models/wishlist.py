from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .user import User


class Wishlist(SQLModel, table=True):
    __tablename__ = "wishlists"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)

    # Relationship to wishlist items
    items: list["WishlistItem"] = Relationship(
        back_populates="wishlist", sa_relationship_kwargs={"lazy": "selectin"}
    )

    # Relationship to User (optional, for backref)
    user: Optional["User"] = Relationship(back_populates="wishlist")


class WishlistItem(SQLModel, table=True):
    __tablename__ = "wishlist_items"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    wishlist_id: UUID = Field(foreign_key="wishlists.id", nullable=False, index=True)
    product_id: UUID = Field(foreign_key="products.id", nullable=False, index=True)

    # Relationships
    wishlist: Optional["Wishlist"] = Relationship(back_populates="items")
