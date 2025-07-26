from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from uuid import UUID
from src.products.schemas import (
    ProductCreate,
    ProductRead,
    ProductReadDetail,
    ProductUpdate,
)
from src.products.service import ProductService
from src.core.dependencies import DbSession, RoleChecker
from src.users.schemas import UserRole

router = APIRouter(prefix="/products", tags=["Products"])

role_checker_admin = Depends(RoleChecker([UserRole.admin]))

@router.post(
    "/",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
    dependencies=[role_checker_admin],
)
async def create_product(product_data: ProductCreate, db_session: DbSession) -> ProductRead:
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
    summary="List all products",
)
async def list_products(db_session: DbSession) -> list[ProductRead]:
    return await ProductService.list_products(db_session)


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
