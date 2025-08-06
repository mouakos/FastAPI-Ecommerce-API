from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AddressBase(BaseModel):
    firstname: str = Field(..., description="First name of the address owner")
    lastname: str = Field(..., description="Last name of the address owner")
    company: Optional[str] = Field(
        default=None, description="Company name of the address owner"
    )
    phone: Optional[str] = Field(
        default=None, description="Phone number of the address owner"
    )
    street: str = Field(..., description="Street address")
    city: str = Field(..., description="City of the address")
    state: Optional[str] = Field(default=None, description="State of the address")
    zip_code: str = Field(..., description="ZIP code of the address")
    country: str = Field(..., description="Country of the address")
    is_default_shipping: bool = Field(
        default=False, description="Is this the default shipping address?"
    )
    is_default_billing: bool = Field(
        default=False, description="Is this the default billing address?"
    )


class AddressCreate(AddressBase):
    pass


class AddressUpdate(BaseModel):
    firstname: Optional[str] = Field(
        default=None, description="First name of the address owner"
    )
    lastname: Optional[str] = Field(
        default=None, description="Last name of the address owner"
    )
    company: Optional[str] = Field(
        default=None, description="Company name of the address owner"
    )
    phone: Optional[str] = Field(
        default=None, description="Phone number of the address owner"
    )
    street: Optional[str] = Field(default=None, description="Street address")
    city: Optional[str] = Field(default=None, description="City of the address")
    state: Optional[str] = Field(default=None, description="State of the address")
    zip_code: Optional[str] = Field(default=None, description="ZIP code of the address")
    country: Optional[str] = Field(default=None, description="Country of the address")
    is_default_shipping: Optional[bool] = Field(
        default=None, description="Is this the default shipping address?"
    )
    is_default_billing: Optional[bool] = Field(
        default=None, description="Is this the default billing address?"
    )


class AddressRead(AddressBase):
    id: int = Field(..., description="Unique identifier for the address")
    user_id: int = Field(..., description="ID of the user who owns this address")
    created_at: datetime = Field(
        ..., description="Timestamp when the address was created"
    )
    updated_at: datetime = Field(
        ..., description="Timestamp when the address was last updated"
    )
