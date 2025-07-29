from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4
from datetime import datetime

if TYPE_CHECKING:
    from app.models.user import User


class Address(SQLModel, table=True):
    __tablename__ = "addresses"
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    street: str = Field(nullable=False)
    city: str = Field(nullable=False)
    state: Optional[str] = Field(default=None, nullable=True)
    zip_code: str = Field(nullable=False)
    country: str = Field(nullable=False)
    is_default: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship to User (optional, for backref)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    user: Optional["User"] = Relationship(back_populates="addresses")
