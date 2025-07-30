from fastapi import APIRouter, status, Depends
from typing import List
from uuid import UUID

from app.dependencies import DbSession, CurrentUser, RoleChecker
from app.addresses.schemas import AddressCreate, AddressUpdate, AddressRead
from app.addresses.service import AddressService
from app.users.schemas import UserRole
from app.exceptions import AuthorizationError

router = APIRouter(prefix="/api/v1/addresses", tags=["Addresses"])


# User endpoints
@router.post(
    "/",
    response_model=AddressRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add new address for current user",
)
async def add_new_address(
    data: AddressCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    return await AddressService.create_address(db, current_user.id, data)


@router.get(
    "/me",
    response_model=List[AddressRead],
    summary="List current user's addresses",
)
async def list_my_addresses(
    db: DbSession,
    current_user: CurrentUser,
):
    return await AddressService.list_addresses_by_user(db, current_user.id)


@router.get(
    "/me/{address_id}",
    response_model=AddressRead,
    summary="Get current user's address by ID",
)
async def get_my_address(
    address_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
):
    address = await AddressService.get_address(db, address_id)
    if address.user_id != current_user.id:
        raise AuthorizationError("Not authorized to access this address.")
    return address


@router.patch(
    "/me/{address_id}",
    response_model=AddressRead,
    summary="Update current user's address by ID",
)
async def update_my_address(
    address_id: UUID,
    data: AddressUpdate,
    db: DbSession,
    current_user: CurrentUser,
):
    address = await AddressService.get_address(db, address_id)
    if address.user_id != current_user.id:
        raise AuthorizationError("Not authorized to update this address.")
    return await AddressService.update_address(db, address_id, data)


@router.delete(
    "/me/{address_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete current user's address by ID",
)
async def delete_my_address(
    address_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
):
    address = await AddressService.get_address(db, address_id)
    if address.user_id != current_user.id:
        raise AuthorizationError("Not authorized to delete this address.")
    await AddressService.delete_address(db, address_id)


# Admin endpoints
role_checker_admin = Depends(RoleChecker([UserRole.admin]))


@router.get(
    "/user/{user_id}",
    response_model=List[AddressRead],
    summary="List addresses by user (admin)",
    dependencies=[role_checker_admin],
)
async def list_addresses_by_user(
    user_id: UUID,
    db: DbSession,
):
    return await AddressService.list_addresses_by_user(db, user_id)


@router.get(
    "/{address_id}",
    response_model=AddressRead,
    summary="Get address by ID (admin)",
    dependencies=[role_checker_admin],
)
async def get_address(
    address_id: UUID,
    db: DbSession,
):
    return await AddressService.get_address(db, address_id)


@router.patch(
    "/{address_id}",
    response_model=AddressRead,
    summary="Update address (admin)",
    dependencies=[role_checker_admin],
)
async def update_address(
    address_id: UUID,
    data: AddressUpdate,
    db: DbSession,
):
    return await AddressService.update_address(db, address_id, data)


@router.delete(
    "/{address_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete address (admin)",
    dependencies=[role_checker_admin],
)
async def delete_address(
    address_id: UUID,
    db: DbSession,
):
    await AddressService.delete_address(db, address_id)
