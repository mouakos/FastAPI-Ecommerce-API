from enum import Enum
from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime, date
from uuid import UUID, uuid4


class Gender(str, Enum):
    male = "male"
    female = "female"
    other = "other"


class UserRole(str, Enum):
    customer = "customer"
    admin = "admin"


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(index=True, nullable=False, unique=True)
    password_hash: str = Field(nullable=False, exclude=True)
    full_name: str = Field(nullable=False)
    gender: Gender = Field(nullable=False)
    date_of_birth: Optional[date] = Field(default=None, nullable=True)
    phone_number: Optional[str] = Field(default=None, nullable=True)
    role: UserRole = Field(default=UserRole.customer, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
