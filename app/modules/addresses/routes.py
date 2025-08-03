from fastapi import APIRouter, status, Depends
from typing import Annotated, List
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database.core import get_session
from app.modules.auth.dependencies import AccessToken, RoleChecker
from .schemas import AddressCreate, AddressUpdate, AddressRead
from .service import AddressService

router = APIRouter(prefix="/api/v1/users", tags=["Addresses"])

DbSession = Annotated[AsyncSession, Depends(get_session)]

# User endpoints
@router.post("/me/addresses", response_model=AddressRead, status_code=status.HTTP_201_CREATED)
async def create_my_address(
    data: AddressCreate,
    db: DbSession,
    token_data: AccessToken,
):
    return await AddressService.create_address(db, token_data.get_uuid(), data)


@router.get("/me/addresses", response_model=List[AddressRead])
async def list_my_addresses(
    token_data: AccessToken,
    db: DbSession,
):
    return await AddressService.list_addresses_by_user(db, token_data.get_uuid())


@router.get("/me/addresses/{address_id}", response_model=AddressRead)
async def get_my_address(
    address_id: UUID,
    db: DbSession,
    token_data: AccessToken,
):
    address = await AddressService.get_address(db, token_data.get_uuid(), address_id)
    return address


@router.patch("/me/addresses/{address_id}", response_model=AddressRead)
async def update_my_address(
    address_id: UUID,
    data: AddressUpdate,
    db: DbSession,
    token_data: AccessToken,
):
    return await AddressService.update_address(db, token_data.get_uuid(), address_id, data)

@router.delete("/me/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_address(
    address_id: UUID,
    db: DbSession,
    token_data: AccessToken,
):
    await AddressService.delete_address(db, token_data.get_uuid(), address_id)


# Admin endpoints
role_checker_admin = Depends(RoleChecker(["admin"]))
admin_router = APIRouter(prefix="/api/v1/admin/users/", tags=["Admin User Addresses"])


@admin_router.get(
    "/",
    response_model=List[AddressRead],
    dependencies=[role_checker_admin],
)
async def list_addresses_by_user(
    user_id: UUID,
    db: DbSession,
):
    return await AddressService.list_addresses_by_user(db, user_id)


@admin_router.get(
    "/{user_id}/addresses/{address_id}", response_model=AddressRead, dependencies=[role_checker_admin]
)
async def get_address(
    user_id: UUID,
    address_id: UUID,
    db: DbSession,
):
    return await AddressService.get_address(db, user_id, address_id)


@admin_router.patch(
    "/{user_id}/addresses/{address_id}", response_model=AddressRead, dependencies=[role_checker_admin]
)
async def update_address(
    user_id: UUID,
    address_id: UUID,
    data: AddressUpdate,
    db: DbSession,
):
    return await AddressService.update_address(db, user_id, address_id, data)


@admin_router.delete(
    "/{user_id}/addresses/{address_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[role_checker_admin],
)
async def delete_address(
    user_id: UUID,
    address_id: UUID,
    db: DbSession,
):
    await AddressService.delete_address(db, user_id, address_id)
