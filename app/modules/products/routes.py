from typing import Optional, Annotated
from fastapi import APIRouter, Depends, Query, status
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession

from app.utils.paginate import PaginatedResponse
from app.database.core import get_session
from app.modules.auth.dependencies import RoleChecker
from .service import ProductService
from .schemas import ProductCreate, ProductRead, ProductReadDetail, ProductUpdate

router = APIRouter(prefix="/products", tags=["Products"])

role_checker_admin = Depends(RoleChecker(["admin"]))

DbSession = Annotated[AsyncSession, Depends(get_session)]


@router.get("/{product_id}", response_model=ProductReadDetail)
async def get_product(product_id: UUID, db_session: DbSession) -> ProductReadDetail:
    return await ProductService.get_product(db_session, product_id)


@router.get("/", response_model=list[ProductRead])
async def list_products(
    db_session: DbSession,
    page: int = Query(default=1, ge=1, description="Page number for pagination"),
    page_size: int = Query(
        default=10, ge=1, le=100, description="Number of products per page"
    ),
    min_price: Optional[float] = Query(
        default=0, ge=0, description="Minimum product price"
    ),
    max_price: Optional[float] = Query(
        default=0, ge=0, description="Maximum product price"
    ),
    brand: Optional[str] = Query(default="", description="Filter products by brand"),
    name: Optional[str] = Query(default="", description="Search products by name"),
    category: Optional[str] = Query(
        default=None, description="Filter products by category"
    ),
    tags: Optional[list[str]] = Query(
        default=None, description="Filter products by tags"
    ),
) -> PaginatedResponse[ProductRead]:
    return await ProductService.list_products(
        db_session,
        page=page,
        page_size=page_size,
        name=name,
        brand=brand,
        is_active=True,
        min_price=min_price,
        max_price=max_price,
        category_id=category,
        tag_ids=tags,
    )


@router.post(
    "/",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[role_checker_admin],
)
async def create_product(
    product_data: ProductCreate, db_session: DbSession
) -> ProductRead:
    return await ProductService.create_product(db_session, product_data)


@router.get(
    "/all/",
    response_model=list[ProductRead],
    dependencies=[role_checker_admin],
)
async def list_all_products(
    db_session: DbSession,
    page: int = Query(default=1, ge=1, description="Page number for pagination"),
    page_size: int = Query(
        default=10, ge=1, le=100, description="Number of products per page"
    ),
    min_price: Optional[float] = Query(
        default=0, ge=0, description="Minimum product price"
    ),
    max_price: Optional[float] = Query(
        default=0, ge=0, description="Maximum product price"
    ),
    brand: Optional[str] = Query(default="", description="Filter products by brand"),
    name: Optional[str] = Query(default="", description="Search products by name"),
    category: Optional[str] = Query(
        default=None, description="Filter products by category"
    ),
    tags: Optional[list[str]] = Query(
        default=None, description="Filter products by tags"
    ),
    is_active: Optional[bool] = Query(
        default=None, description="Filter by active status"
    ),
) -> PaginatedResponse[ProductRead]:
    return await ProductService.list_products(
        db_session,
        page=page,
        page_size=page_size,
        name=name,
        brand=brand,
        is_active=is_active,
        min_price=min_price,
        max_price=max_price,
        category=category,
        tags=tags,
    )


@router.patch(
    "/{product_id}",
    response_model=ProductRead,
    dependencies=[role_checker_admin],
)
async def update_product(
    product_id: UUID, update_data: ProductUpdate, db_session: DbSession
) -> ProductRead:
    return await ProductService.update_product(db_session, product_id, update_data)


@router.delete(
    "/{product_id}",
    dependencies=[role_checker_admin],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def admin_delete_product(product_id: UUID, db_session: DbSession) -> None:
    await ProductService.delete_product(db_session, product_id)
