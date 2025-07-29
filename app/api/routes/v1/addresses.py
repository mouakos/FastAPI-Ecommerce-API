from fastapi import APIRouter, HTTPException, status
from typing import List
from uuid import UUID

from app.api.dependencies import DbSession, CurrentUser
from app.addresses.schemas import AddressCreate, AddressUpdate, AddressRead
from app.addresses.service import AddressService

router = APIRouter(prefix="/api/v1/addresses", tags=["Addresses"])


@router.post(
    "/",
    response_model=AddressRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new address",
)
async def create_address(
    data: AddressCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    address = await AddressService.create_address(db, current_user.id, data)
    return address


@router.get("/{address_id}", response_model=AddressRead, summary="Get address details")
async def get_address(
    address_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
):
    address = await AddressService.get_address(db, address_id, current_user.id)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return address


@router.get(
    "/user/{user_id}",
    response_model=List[AddressRead],
    summary="List addresses by user",
)
async def list_addresses_by_user(
    user_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
):
    return await AddressService.list_addresses_by_user(db, user_id)


@router.patch(
    "/{address_id}", response_model=AddressRead, summary="Update address details"
)
async def update_address(
    address_id: UUID,
    address_in: AddressUpdate,
    db: DbSession,
    current_user: CurrentUser,
):
    address = await AddressService.update_address(db, address_id, address_in)
    return address


@router.delete(
    "/{address_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete address"
)
async def delete_address(
    address_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
):
    await AddressService.delete_address(db, address_id)
