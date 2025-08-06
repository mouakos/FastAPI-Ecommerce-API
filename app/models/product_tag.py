from sqlmodel import SQLModel, Field


class ProductTag(SQLModel, table=True):
    __tablename__ = "product_tags"

    product_id: int = Field(foreign_key="products.id", primary_key=True, nullable=False)
    tag_id: int = Field(foreign_key="tags.id", primary_key=True, nullable=False)
