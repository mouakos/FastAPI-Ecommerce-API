from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func
from uuid import UUID
from datetime import datetime
from slugify import slugify

from src.models.category import Category
from src.models.product import Product
from src.models.tag import Tag
from src.products.schemas import ProductCreate, ProductRead, ProductUpdate
from src.core.exceptions import (
    ProductAlreadyExists,
    ProductNotFound,
    CategoryNotFound,
    TagNotFound,
)


class ProductService:
    @staticmethod
    async def create_product(db: AsyncSession, data: ProductCreate) -> ProductRead:
        """Create a new product.

        Args:
            db (AsyncSession): The database session.
            data (ProductCreate): Data to create the product.

        Returns:
            ProductRead: The created product.

        Raises:
            ProductAlreadyExists: If a product with the same SKU already exists.
            CategoryNotFound: If the category does not exist.
        """
        async with db.begin():
            # Check for existing name/sku
            exists = await db.exec(
                select(Product).where(
                    (
                        (func.lower(Product.name) == data.name.lower())
                        | (func.lower(Product.sku) == data.sku.lower())
                    )
                )
            )
            if exists.first():
                raise ProductAlreadyExists()

            # Check category
            category = await db.get(Category, data.category_id)
            if not category:
                raise CategoryNotFound()

            # Check tags
            tags = []
            if data.tag_ids:
                tags = (
                    await db.exec(select(Tag).where(Tag.id.in_(data.tag_ids)))
                ).all()
                if len(tags) != len(set(data.tag_ids)):
                    raise TagNotFound()

            product = Product(
                **data.model_dump(exclude={"tag_ids"}),
                slug=slugify(data.name),
                tags=tags,
            )
            db.add(product)

        await db.refresh(product)
        return ProductRead(**product.model_dump(), tag_ids=tags)

    @staticmethod
    async def get_product_by_id(db: AsyncSession, product_id: UUID) -> ProductRead:
        """Get a product by its ID.

        Args:
            db (AsyncSession): The database session.
            product_id (UUID): The ID of the product.

        Returns:
            ProductRead: The requested product.

        Raises:
            ProductNotFound: If the product does not exist.
        """
        product = await db.get(Product, product_id)
        if not product:
            raise ProductNotFound()
        return ProductRead(**product.model_dump())

    @staticmethod
    async def list_products(db: AsyncSession) -> list[ProductRead]:
        """List all products.

        Args:
            db (AsyncSession): The database session.

        Returns:
            list[ProductRead]: A list of all products.
        """
        result = await db.exec(select(Product))
        return [ProductRead(**prod.model_dump()) for prod in result.all()]

    @staticmethod
    async def update_product(
        db: AsyncSession, product_id: UUID, data: ProductUpdate
    ) -> ProductRead:
        """Update an existing product.

        Args:
            db (AsyncSession): The database session.
            product_id (UUID): The ID of the product to update.
            data (ProductUpdate): Fields to update.

        Returns:
            ProductRead: The updated product.

        Raises:
            ProductNotFound: If the product does not exist.
            ProductAlreadyExists: If a product with the same SKU already exists.
            CategoryNotFound: If the category does not exist.
        """
        async with db.begin():
            if data.category_id and not await db.get(Category, data.category_id):
                raise CategoryNotFound()

            product = await db.get(Product, product_id)
            if not product:
                raise ProductNotFound()

            if data.name and data.name.lower() != product.name.lower():
                name_exists = await db.exec(
                    select(Product).where(
                        func.lower(Product.name) == data.name.lower(),
                        Product.id != product_id,
                    )
                )
                if name_exists.first():
                    raise ProductAlreadyExists()
                product.slug = slugify(product.name)

            if data.sku and data.sku.lower() != product.sku.lower():
                sku_exists = await db.exec(
                    select(Product).where(
                        func.lower(Product.sku) == data.sku.lower(),
                        Product.id != product_id,
                    )
                )
                if sku_exists.first():
                    raise ProductAlreadyExists()

            for key, value in data.model_dump(
                exclude_unset=True, exclude={"tag_ids"}
            ).items():
                setattr(product, key, value)

            if data.tag_ids:
                tags = (
                    await db.exec(select(Tag).where(Tag.id.in_(data.tag_ids)))
                ).all()
                if len(tags) != len(set(data.tag_ids)):
                    raise TagNotFound()
                product.tags = tags

            # TODO - Check if fields are actually changed
            product.updated_at = datetime.utcnow()

        await db.refresh(product)
        return ProductRead(**product.model_dump(), tag_ids=data.tag_ids or [])

    @staticmethod
    async def delete_product(db: AsyncSession, product_id: UUID) -> None:
        """Delete a product.

        Args:
            db (AsyncSession): The database session.
            product_id (UUID): The ID of the product to delete.

        Raises:
            ProductNotFound: If the product does not exist.
        """
        async with db.begin():
            product = await db.get(Product, product_id)
            if not product:
                raise ProductNotFound()
            await db.delete(product)
