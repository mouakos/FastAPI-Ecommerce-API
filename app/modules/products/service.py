from math import ceil
from typing import Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func
from uuid import UUID
from slugify import slugify

from app.exceptions import NotFoundError, ConflictError
from app.modules.categories.service import CategoryService
from app.utils.paginate import PaginatedResponse
from app.models.product import Product
from .schemas import (
    ProductCreate,
    ProductRead,
    ProductReadDetail,
    ProductUpdate,
)


class ProductService:
    @staticmethod
    async def list_products(
        db: AsyncSession,
        page: int,
        page_size: int,
        min_price: Optional[float],
        max_price: Optional[float],
        brand: Optional[str],
        name: Optional[str],
        category: Optional[str],
        tags: Optional[list[str]],
        is_active: bool,
    ) -> PaginatedResponse[ProductRead]:
        """List products with pagination and filtering.

        Args:
            db (AsyncSession): The database session.
            page (int): The page number for pagination.
            page_size (int): The number of products per page.
            name (Optional[str]): Search term to filter products by name.
            min_price (Optional[float]): Minimum price to filter products.
            max_price (Optional[float]): Maximum price to filter products.
            brand (Optional[str]): Filter products by brand.
            category (Optional[str]): Filter products by category ID.
            tags (Optional[list[str]]): Filter products by tag IDs.
            is_active (bool): Filter by active status.

        Returns:
            PaginatedResponse[ProductRead]: A paginated response containing the list of products.
        """
        filters = ProductService._build_product_filters(
            name, is_active, min_price, max_price, brand, category, tags
        )

        # Get total count
        count_stmt = select(func.count()).select_from(Product).where(*filters)
        total = (await db.exec(count_stmt)).one()

        # Get paginated products
        stmt = (
            select(Product)
            .where(*filters)
            .order_by(Product.name)
            .limit(page_size)
            .offset((page - 1) * page_size)
        )
        products = (await db.exec(stmt)).all()

        return PaginatedResponse[ProductRead](
            total=total,
            page=page,
            size=page_size,
            pages=ceil(total / page_size) if total else 1,
            items=products,
        )

    @staticmethod
    async def create_product(db: AsyncSession, data: ProductCreate) -> ProductRead:
        """Create a new product.

        Args:
            db (AsyncSession): The database session.
            data (ProductCreate): Data to create the product.
        Raises:
            ConflictError: If a product with the same name or SKU already exists.
            NotFoundError: If the category or tags do not exist.

        Returns:
            ProductRead: The created product.
        """

        # Check for existing name/sku
        if await ProductService._check_product_existence(db, data.name, data.sku):
            raise ConflictError(
                f"Product with name {data.name} or SKU {data.sku} already exists."
            )

        # Check category
        _ = await CategoryService.get_category(db, data.category_id)

        product = Product(
            **data.model_dump(),
            slug=slugify(data.name),
        )
        db.add(product)
        await db.commit()

        return product

    @staticmethod
    async def get_product(db: AsyncSession, product_id: UUID) -> ProductReadDetail:
        """Get a product by its ID.

        Args:
            db (AsyncSession): The database session.
            product_id (UUID): The ID of the product.

        Raises:
            NotFoundError: If the product does not exist.

        Returns:
            ProductReadDetail: The product details.
        """
        product = await db.get(Product, product_id)
        if not product:
            raise NotFoundError(f"Product with ID {product_id} not found.")
        return product

    @staticmethod
    async def update_product(
        db: AsyncSession, product_id: UUID, data: ProductUpdate
    ) -> ProductRead:
        """Update an existing product.

        Args:
            db (AsyncSession): The database session.
            product_id (UUID): The ID of the product to update.
            data (ProductUpdate): Fields to update.

        Raises:
            NotFoundError: If the product or category do not exist.
            ConflictError: If a product with the same name or SKU already exists.
        Returns:
            ProductRead: The updated product.
        """

        _ = await CategoryService.get_category(db, data.category_id)

        product = await db.get(Product, product_id)
        if not product:
            raise NotFoundError(f"Product with ID {product_id} not found.")

        if data.name and data.name.lower() != product.name.lower():
            if await ProductService._check_name_conflict(db, data.name, product_id):
                raise ConflictError(f"Product with name {data.name} already exists.")
            product.slug = slugify(data.name)

        if data.sku and data.sku.lower() != product.sku.lower():
            if await ProductService._check_sku_conflict(db, data.sku, product_id):
                raise ConflictError(f"Product with SKU {data.sku} already exists.")

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(product, key, value)

        await db.commit()
        return product

    @staticmethod
    async def delete_product(db: AsyncSession, product_id: UUID) -> None:
        """Delete a product.

        Args:
            db (AsyncSession): The database session.
            product_id (UUID): The ID of the product to delete.

        Raises:
            NotFoundError: If the product does not exist.
        """

        product = await db.get(Product, product_id)
        if not product:
            raise NotFoundError(f"Product with ID {product_id} not found.")
        await db.delete(product)
        await db.commit()

    @staticmethod
    async def _check_product_existence(db: AsyncSession, name: str, sku: str) -> bool:
        exists = await db.exec(
            select(Product).where(
                (
                    (func.lower(Product.name) == name.lower())
                    | (func.lower(Product.sku) == sku.lower())
                )
            )
        )

        return exists.first() is not None

    @staticmethod
    def _build_product_filters(
        name: Optional[str],
        is_active: Optional[bool],
        min_price: Optional[float],
        max_price: Optional[float],
        brand: Optional[str],
        category: Optional[str],
        tags: Optional[list[str]],
    ):
        filters = []
        if name:
            filters.append(Product.name.ilike(f"%{name}%"))
        if is_active is not None:
            filters.append(Product.is_active == is_active)
        if min_price is not None:
            filters.append(Product.price >= min_price)
        if max_price is not None:
            filters.append(Product.price <= max_price)
        if brand:
            filters.append(Product.brand.ilike(f"%{brand}%"))
        if category:
            filters.append(Product.category.name.ilike(f"%{category}%"))
        if tags:
            filters.append(Product.tags.any(name__in=tags))
        return filters

    @staticmethod
    async def _check_name_conflict(
        db: AsyncSession, name: str, exclude_id: UUID
    ) -> bool:
        conflict = await db.exec(
            select(Product).where(
                func.lower(Product.name) == name.lower(),
                Product.id != exclude_id,
            )
        )
        return conflict.first() is not None

    @staticmethod
    async def _check_sku_conflict(db: AsyncSession, sku: str, exclude_id: UUID) -> bool:
        conflict = await db.exec(
            select(Product).where(
                func.lower(Product.sku) == sku.lower(),
                Product.id != exclude_id,
            )
        )
        return conflict.first() is not None
