from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.exceptions import NotFoundError
from app.models.address import Address
from app.addresses.schemas import AddressCreate, AddressRead, AddressUpdate


class AddressService:
    @staticmethod
    async def create_address(
        db: AsyncSession, user_id: UUID, data: AddressCreate
    ) -> AddressRead:
        """Create a new address for a user.

        Args:
            db (AsyncSession): The database session.
            user_id (UUID): The ID of the user to create the address for.
            data (AddressCreate): The data for the new address.
        Raises:
            NotFoundError: If an address with the same details already exists for the user.
        Returns:
            AddressRead: The created address.
        """

        if data.is_default_shipping:
            await AddressService._unset_default_shipping(db, user_id)

        if data.is_default_billing:
            await AddressService._unset_default_billing(db, user_id)

        address = Address(**data.model_dump())
        db.add(address)
        await db.commit()
        return address

    @staticmethod
    async def get_address(db: AsyncSession, address_id: UUID) -> AddressRead:
        """Get an address by its ID.

        Args:
            db (AsyncSession): The database session.
            address_id (UUID): The ID of the address to retrieve.

        Raises:
            NotFoundError: If the address is not found.

        Returns:
            AddressRead: The retrieved address.
        """
        result = await db.get(Address, address_id)
        if not result:
            raise NotFoundError(f"Address with ID {address_id} not found")
        return result

    @staticmethod
    async def list_addresses_by_user(
        db: AsyncSession, user_id: UUID
    ) -> list[AddressRead]:
        """List all addresses for a user.

        Args:
            db (AsyncSession): The database session.
            user_id (UUID): The ID of the user to list addresses for.

        Returns:
            list[AddressRead]: The list of addresses for the user.
        """
        result = await db.exec(
            select(Address)
            .where(Address.user_id == user_id)
            .order_by(Address.created_at.desc())
        )
        return result.all()

    @staticmethod
    async def update_address(
        db: AsyncSession, address_id: UUID, data: AddressUpdate
    ) -> AddressRead:
        """Update an existing address.

        Args:
            db (AsyncSession): The database session.
            address_id (UUID): The ID of the address to update.
            data (AddressUpdate): The updated data for the address.

        Raises:
            NotFoundError: If the address is not found.

        Returns:
            AddressRead: The updated address.
        """
        address = await db.get(Address, address_id)
        if not address:
            raise NotFoundError(f"Address with ID {address_id} not found")

        update_data = data.model_dump(exclude_unset=True)

        if data.is_default_shipping:
            await AddressService._unset_default_shipping(db, address.user_id)

        if data.is_default_billing:
            await AddressService._unset_default_billing(db, address.user_id)

        for key, value in update_data.items():
            setattr(address, key, value)
        await db.commit()
        return address

    @staticmethod
    async def delete_address(db: AsyncSession, address_id: UUID) -> None:
        """Delete an address by its ID.

        Args:
            db (AsyncSession): The database session.
            address_id (UUID): The ID of the address to delete.

        Raises:
            NotFoundError: If the address is not found.
        """

        address = await db.get(Address, address_id)
        if not address:
            raise NotFoundError(f"Address with ID {address_id} not found")
        await db.delete(address)
        await db.commit()

    @staticmethod
    async def _unset_default_billing(db, user_id: UUID):
        await db.exec(
            select(Address)
            .where(Address.user_id == user_id)
            .values(is_default_billing=False)
        )

    @staticmethod
    async def _unset_default_shipping(db, user_id: UUID):
        await db.exec(
            select(Address)
            .where(Address.user_id == user_id)
            .values(is_default_shipping=False)
        )
