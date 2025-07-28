from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from uuid import UUID
from app.products.schemas import (
    ProductCreate,
    ProductRead,
    ProductReadDetail,
    ProductUpdate,
)
from app.products.service import ProductService
from app.core.dependencies import DbSession, RoleChecker
from app.users.schemas import UserRole
from app.utils.paginate import PaginatedResponse

router = APIRouter(prefix="/products", tags=["Products"])

role_checker_admin = Depends(RoleChecker([UserRole.admin]))


@router.post(
    "/",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
    dependencies=[role_checker_admin],
)
async def create_product(
    product_data: ProductCreate, db_session: DbSession
) -> ProductRead:
    return await ProductService.create_product(db_session, product_data)


@router.get(
    "/{product_id}",
    response_model=ProductReadDetail,
    summary="Get product by ID",
)
async def get_product(product_id: UUID, db_session: DbSession) -> ProductReadDetail:
    return await ProductService.get_product(db_session, product_id)


@router.get(
    "/",
    response_model=list[ProductRead],
    summary="List products",
)
async def list_products(
    db_session: DbSession,
    page: int = Query(default=1, ge=1, description="Page number for pagination"),
    page_size: int = Query(
        default=10, ge=1, le=100, description="Number of products per page"
    ),
    search: Optional[str] = Query(default="", description="Search products by name"),
) -> PaginatedResponse[ProductRead]:
    return await ProductService.list_products(
        db_session, page=page, page_size=page_size, search=search, is_active=True
    )


@router.get(
    "/admin/",
    response_model=list[ProductRead],
    summary="List all products",
)
async def list_all_products(
    db_session: DbSession,
    page: int = Query(default=1, ge=1, description="Page number for pagination"),
    page_size: int = Query(
        default=10, ge=1, le=100, description="Number of products per page"
    ),
    search: Optional[str] = Query(default="", description="Search products by name"),
    is_active: Optional[bool] = Query(
        default=None, description="Filter by active status"
    ),
) -> PaginatedResponse[ProductRead]:
    return await ProductService.list_products(
        db_session, page=page, page_size=page_size, search=search, is_active=is_active
    )


@router.patch(
    "/{product_id}",
    response_model=ProductRead,
    summary="Update an existing product",
    dependencies=[role_checker_admin],
)
async def update_product(
    product_id: UUID, update_data: ProductUpdate, db_session: DbSession
) -> ProductRead:
    return await ProductService.update_product(db_session, product_id, update_data)


@router.delete(
    "/{product_id}",
    summary="Delete an existing product",
    dependencies=[role_checker_admin],
)
async def delete_product(product_id: UUID, db_session: DbSession) -> JSONResponse:
    await ProductService.delete_product(db_session, product_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Product deleted successfully"},
    )
