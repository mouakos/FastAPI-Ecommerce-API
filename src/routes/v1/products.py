from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from uuid import UUID
from src.products.schemas import ProductCreate, ProductRead, ProductUpdate
from src.products.service import ProductService
from src.core.dependencies import DbSession

router = APIRouter(prefix="/products", tags=["Products"])


@router.post(
    "/",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
)
async def create_product(product_data: ProductCreate, db: DbSession) -> ProductRead:
    return await ProductService.create_product(db, product_data)


@router.get(
    "/{product_id}",
    response_model=ProductRead,
    summary="Get product by ID",
)
async def get_product_by_id(product_id: UUID, db: DbSession) -> ProductRead:
    return await ProductService.get_product_by_id(db, product_id)


@router.get(
    "/",
    response_model=list[ProductRead],
    summary="List all products",
)
async def list_products(db: DbSession) -> list[ProductRead]:
    return await ProductService.list_products(db)


@router.patch(
    "/{product_id}",
    response_model=ProductRead,
    summary="Update an existing product",
)
async def update_product(
    product_id: UUID, update_data: ProductUpdate, db: DbSession
) -> ProductRead:
    return await ProductService.update_product(db, product_id, update_data)


@router.delete(
    "/{product_id}",
    summary="Delete an existing product",
)
async def delete_product(product_id: UUID, db: DbSession) -> JSONResponse:
    await ProductService.delete_product(db, product_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Product deleted successfully"},
    )
