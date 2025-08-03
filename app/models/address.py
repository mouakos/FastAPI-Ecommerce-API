from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from .user import User


class Address(SQLModel, table=True):
    __tablename__ = "addresses"
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    firstname: str = Field(nullable=False)
    lastname: str = Field(nullable=False)
    company: Optional[str] = Field(default=None, nullable=True)
    phone: Optional[str] = Field(default=None, nullable=True)
    street: str = Field(nullable=False)
    city: str = Field(nullable=False)
    state: Optional[str] = Field(default=None, nullable=True)
    zip_code: str = Field(nullable=False)
    country: str = Field(nullable=False)
    is_default_shipping: bool = Field(default=False)
    is_default_billing: bool = Field(default=False)

    # Relationship to User (optional, for backref)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    user: Optional["User"] = Relationship(back_populates="addresses")
