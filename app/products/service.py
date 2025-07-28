from math import ceil
from typing import Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func
from uuid import UUID
from datetime import datetime
from slugify import slugify

from app.categories.schemas import CategoryRead
from app.models.category import Category
from app.models.product import Product
from app.models.tag import Tag
from app.products.schemas import (
    ProductCreate,
    ProductRead,
    ProductReadDetail,
    ProductUpdate,
)
from app.core.exceptions import (
    ProductAlreadyExists,
    ProductNotFound,
    CategoryNotFound,
    TagNotFound,
)
from app.reviews.schemas import ReviewRead
from app.tags.schemas import TagRead
from app.utils.paginate import PaginatedResponse


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

        Returns:
            ProductRead: The created product.

        Raises:
            ProductAlreadyExists: If a product with the same SKU already exists.
            CategoryNotFound: If the category does not exist.
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
                raise ProductAlreadyExists()

            # Check category
            category = await db_session.get(Category, data.category_id)
            if not category:
                raise CategoryNotFound()

            # Check tags
            tags = []
            if data.tag_ids:
                tags = (
                    await db_session.exec(select(Tag).where(Tag.id.in_(data.tag_ids)))
                ).all()
                if len(tags) != len(set(data.tag_ids)):
                    raise TagNotFound()

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

        Returns:
            ProductReadDetail: The product details.

        Raises:
            ProductNotFound: If the product does not exist.
        """
        product = await db_session.get(Product, product_id)
        if not product:
            raise ProductNotFound()
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

        Returns:
            ProductRead: The updated product.

        Raises:
            ProductNotFound: If the product does not exist.
            ProductAlreadyExists: If a product with the same SKU already exists.
            CategoryNotFound: If the category does not exist.
        """

        if data.category_id and not await db_session.get(Category, data.category_id):
            raise CategoryNotFound()

        product = await db_session.get(Product, product_id)
        if not product:
            raise ProductNotFound()

        if data.name and data.name.lower() != product.name.lower():
            name_exists = await db_session.exec(
                select(Product).where(
                    func.lower(Product.name) == data.name.lower(),
                    Product.id != product_id,
                )
            )
            if name_exists.first():
                raise ProductAlreadyExists()
            product.slug = slugify(product.name)

        if data.sku and data.sku.lower() != product.sku.lower():
            sku_exists = await db_session.exec(
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
                await db_session.exec(select(Tag).where(Tag.id.in_(data.tag_ids)))
            ).all()
            if len(tags) != len(set(data.tag_ids)):
                raise TagNotFound()
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
            ProductNotFound: If the product does not exist.
        """
        async with db_session.begin():
            product = await db_session.get(Product, product_id)
            if not product:
                raise ProductNotFound()
            await db_session.delete(product)
