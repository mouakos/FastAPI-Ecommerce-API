from typing import List, Optional
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from fastapi import HTTPException

from app.models.address import Address
from app.addresses.schemas import AddressCreate, AddressUpdate


class AddressService:
    @staticmethod
    async def create_address(
        db: AsyncSession, user_id: UUID, data: AddressCreate
    ) -> Address:
        if data.is_default:
            # Unset previous default for user

            await db.exec(
                select(Address)
                .where(Address.user_id == user_id)
                .values(is_default=False)
            )
        address = Address(**data.model_dump())
        db.add(address)
        await db.commit()
        await db.refresh(address)
        return address

    @staticmethod
    async def get_address(db: AsyncSession, address_id: UUID) -> Optional[Address]:
        result = await db.exec(select(Address).where(Address.id == address_id))
        return result.first()

    @staticmethod
    async def list_addresses_by_user(db: AsyncSession, user_id: UUID) -> List[Address]:
        result = await db.exec(
            select(Address)
            .where(Address.user_id == user_id)
            .order_by(Address.created_at.desc())
        )
        return result.all()

    @staticmethod
    async def update_address(
        db: AsyncSession, address_id: UUID, data: AddressUpdate
    ) -> Address:
        result = await db.exec(select(Address).where(Address.id == address_id))
        address = result.first()
        if not address:
            raise HTTPException(status_code=404, detail="Address not found")
        update_data = data.model_dump(exclude_unset=True)
        if data.is_default:
            # Unset previous default for user
            await db.exec(
                select(Address)
                .where(Address.user_id == address.user_id)
                .values(is_default=False)
            )
        for key, value in update_data.items():
            setattr(address, key, value)
        await db.commit()
        await db.refresh(address)
        return address

    @staticmethod
    async def delete_address(db: AsyncSession, address_id: UUID) -> None:
        result = await db.exec(select(Address).where(Address.id == address_id))
        address = result.first()
        if not address:
            raise HTTPException(status_code=404, detail="Address not found")
        await db.delete(address)
        await db.commit()
