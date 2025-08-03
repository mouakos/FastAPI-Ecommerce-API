from uuid import UUID
from pydantic import BaseModel, Field


class WishlistItemBase(BaseModel):
    product_id: UUID = Field(..., description="ID of the product in the wishlist")


class WishlistItemCreate(WishlistItemBase):
    pass


class WishlistItemRead(WishlistItemBase):
    id: UUID = Field(..., description="Unique identifier of the wishlist item")
    wishlist_id: UUID = Field(
        ..., description="ID of the wishlist this item belongs to"
    )


class WishlistRead(BaseModel):
    id: UUID = Field(..., description="Unique identifier of the wishlist")
    user_id: UUID = Field(..., description="ID of the user who owns the wishlist")
    items: list[WishlistItemRead] = Field(
        default_factory=list, description="List of wishlist items"
    )
