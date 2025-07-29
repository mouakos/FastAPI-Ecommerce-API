from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship


class Wishlist(SQLModel, table=True):
    __tablename__ = "wishlists"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship to wishlist items
    items: List["WishlistItem"] = Relationship(back_populates="wishlist")


class WishlistItem(SQLModel, table=True):
    __tablename__ = "wishlist_items"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    wishlist_id: UUID = Field(foreign_key="wishlists.id", nullable=False, index=True)
    product_id: UUID = Field(foreign_key="products.id", nullable=False, index=True)
    added_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    wishlist: Optional[Wishlist] = Relationship(back_populates="items")
