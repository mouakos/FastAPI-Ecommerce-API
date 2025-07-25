from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    pass


class TagUpdate(TagBase):
    name: Optional[str] = None


class TagRead(TagBase):
    id: UUID
    slug: str
    created_at: datetime
    updated_at: datetime
