from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, update

from app.exceptions import NotFoundError
from app.models.address import Address
from app.modules.users.service import UserService
from .schemas import AddressCreate, AddressRead, AddressUpdate


class AddressService:
    @staticmethod
    async def create_user_address(
        db: AsyncSession, user_id: UUID, data: AddressCreate
    ) -> AddressRead:
        """Create a new address for a user.

        Args:
            db (AsyncSession): The database session.
            user_id (UUID): The ID of the user to create the address for.
            data (AddressCreate): The data for the new address.
        Raises:
            NotFoundError: If the user does not exist.
        Returns:
            AddressRead: The created address.
        """
        user = await db.get(Address, user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")

        if data.is_default_shipping:
            await AddressService._unset_default_flag(db, user_id, "is_default_shipping")

        if data.is_default_billing:
            await AddressService._unset_default_flag(db, user_id, "is_default_billing")

        address = Address(**data.model_dump(), user_id=user_id)
        db.add(address)
        await db.commit()
        return address

    @staticmethod
    async def get_user_address(
        db: AsyncSession, user_id: UUID, address_id: UUID
    ) -> AddressRead:
        """Get an address by its ID for a specific user.

        Args:
            db (AsyncSession): The database session.
            address_id (UUID): The ID of the address to retrieve.
            user_id (UUID): The ID of the user who owns the address.

        Raises:
            NotFoundError: If the user or address is not found.

        Returns:
            AddressRead: The retrieved address.
        """
        user = await UserService.get_user(db, user_id)

        stmt = select(Address).where(
            Address.id == address_id, Address.user_id == user.id
        )
        result = await db.exec(stmt)
        address = result.first()
        if not address:
            raise NotFoundError(
                f"Address with ID {address_id} not found for user {user_id}"
            )
        return address

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
        result = await db.exec(select(Address).where(Address.user_id == user_id))
        return result.all()

    @staticmethod
    async def update_user_address(
        db: AsyncSession, user_id: UUID, address_id: UUID, data: AddressUpdate
    ) -> AddressRead:
        """Update an existing address for a user.

        Args:
            db (AsyncSession): The database session.
            address_id (UUID): The ID of the address to update.
            data (AddressUpdate): The updated data for the address.
            user_id (UUID): The ID of the user who owns the address.

        Raises:
            NotFoundError: If the user or address is not found.

        Returns:
            AddressRead: The updated address.
        """
        user = await UserService.get_user(db, user_id)

        stmt = select(Address).where(
            Address.id == address_id, Address.user_id == user.id
        )
        result = await db.exec(stmt)
        address = result.first()

        if not address:
            raise NotFoundError(
                f"Address with ID {address_id} not found for user {user_id}"
            )

        update_data = data.model_dump(exclude_unset=True)

        if data.is_default_shipping:
            await AddressService._unset_default_flag(
                db, address.user_id, "is_default_shipping"
            )

        if data.is_default_billing:
            await AddressService._unset_default_flag(
                db, address.user_id, "is_default_billing"
            )

        for key, value in update_data.items():
            setattr(address, key, value)

        await db.commit()
        return address

    @staticmethod
    async def delete_user_address(
        db: AsyncSession, user_id: UUID, address_id: UUID
    ) -> None:
        """Delete an address by its ID for a specific user.

        Args:
            db (AsyncSession): The database session.
            address_id (UUID): The ID of the address to delete.
            user_id (UUID): The ID of the user who owns the address.

        Raises:
            NotFoundError: If the user or address is not found.
        """

        user = await UserService.get_user(db, user_id)
        stmt = select(Address).where(
            Address.id == address_id, Address.user_id == user.id
        )
        result = await db.exec(stmt)
        address = result.first()
        if not address:
            raise NotFoundError(
                f"Address with ID {address_id} not found for user {user_id}"
            )

        await db.delete(address)
        await db.commit()

    @staticmethod
    async def _unset_default_flag(db: AsyncSession, user_id: UUID, flag_field: str):
        await db.exec(
            update(Address)
            .where(Address.user_id == user_id)
            .values({flag_field: False})
        )
