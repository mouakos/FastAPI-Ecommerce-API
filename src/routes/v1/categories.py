from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from src.categories.schemas import (
    CategoryCreate,
    CategoryRead,
    CategoryReadDetail,
    CategoryUpdate,
)
from src.core.dependencies import DbSession, RoleChecker
from src.categories.service import CategoryService
from src.users.schemas import UserRole


router = APIRouter(prefix="/api/v1/categories", tags=["Categories"])

role_checker_admin = Depends(RoleChecker([UserRole.admin]))


# --- Public Endpoints ---
@router.get("/", response_model=list[CategoryReadDetail], summary="List all Categories")
async def list_categories(
    db: DbSession,
    parent_id: UUID | None = Query(None),
    depth: int = Query(1, ge=1, le=3),  # Limit recursion depth
):
    return await CategoryService.get_category_tree(db, parent_id, depth)


@router.get(
    "/{category_id}", response_model=CategoryReadDetail, summary="Get Category Details"
)
async def get_category(
    db: DbSession,
    category_id: UUID,
    include_children: bool = False,
):
    return await CategoryService.get_category(
        db,
        category_id,
        include_children=include_children,
    )


# --- Admin Endpoints ---
@router.post(
    "/",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create New Category",
)
async def create_category(
    db: DbSession,
    category_data: CategoryCreate,
):
    return await CategoryService.create_category(db, category_data)


@router.put(
    "/{category_id}",
    response_model=CategoryRead,
    summary="Update Category",
)
async def update_category(
    db: DbSession,
    category_id: UUID,
    update_data: CategoryUpdate,
):
    return await CategoryService.update_category(db, category_id, update_data)


@router.delete(
    "/{category_id}",
    # dependencies=[role_checker_admin],
    summary="Delete Category",
)
async def delete_category(db: DbSession, category_id: UUID) -> JSONResponse:
    await CategoryService.delete_category(db, category_id)
    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content={"message": "Category deleted successfully"},
    )
