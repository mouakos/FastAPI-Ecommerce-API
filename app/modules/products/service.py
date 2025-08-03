from math import ceil
from typing import Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func
from uuid import UUID
from datetime import datetime
from slugify import slugify

from ...exceptions import NotFoundError, ConflictError
from ...utils.paginate import PaginatedResponse
from ...models.category import Category
from ...models.product import Product
from ...models.tag import Tag
from ..categories.schemas import CategoryRead
from ..reviews.schemas import ReviewRead
from ..tags.schemas import TagRead
from .schemas import (
    ProductCreate,
    ProductRead,
    ProductReadDetail,
    ProductUpdate,
)


class ProductService:
    @staticmethod
    async def list_products(
        db_session: AsyncSession,
        page: int,
        page_size: int,
        search: Optional[str],
        is_active: bool,
    ) -> PaginatedResponse[ProductRead]:
        """List products with pagination and filtering.

        Args:
            db_session (AsyncSession): The database session.
            page (int): The page number for pagination.
            page_size (int): The number of products per page.
            search (Optional[str]): Search term to filter products by name.
            is_active (bool): Filter by active status.

        Returns:
            PaginatedResponse[ProductRead]: A paginated response containing the list of products.
        """
        # Get total count (without limit/offset)
        count_stmt = (
            select(func.count())
            .select_from(Product)
            .where(
                (Product.name.ilike(f"%{search}%")) if search else True,
                (Product.is_active == is_active) if is_active is not None else True,
            )
        )
        total = (await db_session.exec(count_stmt)).one()

        # Get paginated products
        result = await db_session.exec(
            select(Product)
            .where(
                (Product.name.ilike(f"%{search}%")) if search else True,
                (Product.is_active == is_active) if is_active is not None else True,
            )
            .order_by(Product.created_at.desc())
            .limit(page_size)
            .offset((page - 1) * page_size)
        )
        products = result.all()

        return PaginatedResponse[ProductRead](
            total=total,
            page=page,
            size=page_size,
            pages=ceil(total / page_size) if total else 1,
            items=[ProductRead(**product.model_dump()) for product in products],
        )

    @staticmethod
    async def create_product(
        db_session: AsyncSession, data: ProductCreate
    ) -> ProductRead:
        """Create a new product.

        Args:
            db_session (AsyncSession): The database session.
            data (ProductCreate): Data to create the product.
        Raises:
            ConflictError: If a product with the same name or SKU already exists.
            NotFoundError: If the category or tags do not exist.

        Returns:
            ProductRead: The created product.
        """
        async with db_session.begin():
            # Check for existing name/sku
            exists = await db_session.exec(
                select(Product).where(
                    (
                        (func.lower(Product.name) == data.name.lower())
                        | (func.lower(Product.sku) == data.sku.lower())
                    )
                )
            )
            if exists.first():
                raise ConflictError(
                    f"Product with name {data.name} or SKU {data.sku} already exists."
                )

            # Check category
            category = await db_session.get(Category, data.category_id)
            if not category:
                raise NotFoundError(f"Category with ID {data.category_id} not found.")

            # Check tags
            tags = []
            if data.tag_ids:
                tags = (
                    await db_session.exec(select(Tag).where(Tag.id.in_(data.tag_ids)))
                ).all()
                if len(tags) != len(set(data.tag_ids)):
                    raise NotFoundError("One or more tags not found.")

            product = Product(
                **data.model_dump(exclude={"tag_ids"}),
                slug=slugify(data.name),
                tags=tags,
            )
            db_session.add(product)

        await db_session.refresh(product)
        return ProductRead(**product.model_dump(), tag_ids=tags)

    @staticmethod
    async def get_product(
        db_session: AsyncSession, product_id: UUID
    ) -> ProductReadDetail:
        """Get a product by its ID.

        Args:
            db_session (AsyncSession): The database session.
            product_id (UUID): The ID of the product.

        Raises:
            NotFoundError: If the product does not exist.

        Returns:
            ProductReadDetail: The product details.
        """
        product = await db_session.get(Product, product_id)
        if not product:
            raise NotFoundError(f"Product with ID {product_id} not found.")

        category_read = (
            CategoryRead(**product.category.model_dump()) if product.category else None
        )
        tags_read = (
            [TagRead(**tag.model_dump()) for tag in product.tags]
            if product.tags
            else []
        )
        reviews_read = (
            [ReviewRead(**review.model_dump()) for review in product.reviews]
            if product.reviews
            else []
        )
        return ProductReadDetail(
            **product.model_dump(),
            category=category_read,
            tags=tags_read,
            reviews=reviews_read,
        )

    @staticmethod
    async def update_product(
        db_session: AsyncSession, product_id: UUID, data: ProductUpdate
    ) -> ProductRead:
        """Update an existing product.

        Args:
            db_session (AsyncSession): The database session.
            product_id (UUID): The ID of the product to update.
            data (ProductUpdate): Fields to update.

        Raises:
            NotFoundError: If the product, category, or tags do not exist.
            ConflictError: If a product with the same name or SKU already exists.
        Returns:
            ProductRead: The updated product.
        """

        if data.category_id and not await db_session.get(Category, data.category_id):
            raise NotFoundError(f"Category with ID {data.category_id} not found.")

        product = await db_session.get(Product, product_id)
        if not product:
            raise NotFoundError(f"Product with ID {product_id} not found.")

        if data.name and data.name.lower() != product.name.lower():
            name_exists = await db_session.exec(
                select(Product).where(
                    func.lower(Product.name) == data.name.lower(),
                    Product.id != product_id,
                )
            )
            if name_exists.first():
                raise ConflictError(f"Product with name {data.name} already exists.")
            product.slug = slugify(product.name)

        if data.sku and data.sku.lower() != product.sku.lower():
            sku_exists = await db_session.exec(
                select(Product).where(
                    func.lower(Product.sku) == data.sku.lower(),
                    Product.id != product_id,
                )
            )
            if sku_exists.first():
                raise ConflictError(f"Product with SKU {data.sku} already exists.")

        for key, value in data.model_dump(
            exclude_unset=True, exclude={"tag_ids"}
        ).items():
            setattr(product, key, value)

        if data.tag_ids:
            tags = (
                await db_session.exec(select(Tag).where(Tag.id.in_(data.tag_ids)))
            ).all()
            if len(tags) != len(set(data.tag_ids)):
                raise NotFoundError("One or more tags not found.")
            product.tags = tags

        # TODO - Check if fields are actually changed
        product.updated_at = datetime.utcnow()

        await db_session.commit()
        await db_session.refresh(product)
        return ProductRead(**product.model_dump(), tag_ids=data.tag_ids or [])

    @staticmethod
    async def delete_product(db_session: AsyncSession, product_id: UUID) -> None:
        """Delete a product.

        Args:
            db_session (AsyncSession): The database session.
            product_id (UUID): The ID of the product to delete.

        Raises:
            NotFoundError: If the product does not exist.
        """
        async with db_session.begin():
            product = await db_session.get(Product, product_id)
            if not product:
                raise NotFoundError(f"Product with ID {product_id} not found.")
            await db_session.delete(product)
