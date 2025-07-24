from typing import Optional
from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime
from uuid import UUID, uuid4


class Category(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True, nullable=False, unique=True)
    slug: str = Field(index=True, nullable=False, unique=True)
    description: Optional[str] = Field(default=None, nullable=True)
    parent_id: Optional[UUID] = Field(
        default=None, foreign_key="category.id", nullable=True
    )

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    parent: Optional["Category"] = Relationship(
        back_populates="children", sa_relationship_kwargs={"remote_side": "Category.id"}
    )
    children: list["Category"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )
