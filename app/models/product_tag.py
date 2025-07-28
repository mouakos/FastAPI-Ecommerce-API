from sqlmodel import SQLModel, Field
from uuid import UUID


class ProductTag(SQLModel, table=True):
    __tablename__ = "product_tags"

    product_id: UUID = Field(foreign_key="products.id", primary_key=True)
    tag_id: UUID = Field(foreign_key="tags.id", primary_key=True)
