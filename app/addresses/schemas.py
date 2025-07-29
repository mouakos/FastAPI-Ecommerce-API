from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class AddressBase(BaseModel):
    street: str = Field(..., description="Street address")
    city: str = Field(..., description="City of the address")
    state: Optional[str] = Field(default=None, description="State of the address")
    zip_code: str = Field(..., description="ZIP code of the address")
    country: str = Field(..., description="Country of the address")
    is_default: bool = Field(default=False, description="Is this the default address?")


class AddressCreate(AddressBase):
    pass


class AddressUpdate(BaseModel):
    street: Optional[str] = Field(default=None, description="Street address")
    city: Optional[str] = Field(default=None, description="City of the address")
    state: Optional[str] = Field(default=None, description="State of the address")
    zip_code: Optional[str] = Field(default=None, description="ZIP code of the address")
    country: Optional[str] = Field(default=None, description="Country of the address")
    is_default: Optional[bool] = Field(
        default=None, description="Is this the default address?"
    )


class AddressRead(AddressBase):
    id: UUID = Field(..., description="Unique identifier for the address")
    user_id: UUID = Field(..., description="ID of the user who owns this address")
    created_at: datetime = Field(
        ..., description="Timestamp when the address was created"
    )
    updated_at: datetime = Field(
        ..., description="Timestamp when the address was last updated"
    )
