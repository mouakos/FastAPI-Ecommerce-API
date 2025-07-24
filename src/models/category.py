from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime
from uuid import UUID, uuid4


class Category(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True, nullable=False, unique=True)
    slug: str = Field(index=True, nullable=False, unique=True)
    description: Optional[str] = Field(default=None, nullable=True)

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
