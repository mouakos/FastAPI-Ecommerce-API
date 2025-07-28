from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from src.categories.schemas import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
)
from src.core.dependencies import DbSession, RoleChecker
from src.categories.service import CategoryService
from src.users.schemas import UserRole
from src.utils.paginate import PaginatedResponse


router = APIRouter(prefix="/api/v1/categories", tags=["Categories"])

role_checker_admin = Depends(RoleChecker([UserRole.admin]))


@router.get(
    "/", response_model=PaginatedResponse[CategoryRead], summary="List Categories"
)
async def list_categories(
    db_session: DbSession,
    page: int = Query(default=1, ge=1, description="Page number for pagination"),
    page_size: int = Query(
        default=10, ge=1, le=100, description="Number of categories per page"
    ),
    search: Optional[str] = Query(default="", description="Search categories by name"),
) -> PaginatedResponse[CategoryRead]:
    return await CategoryService.list_categories(
        db_session, page=page, page_size=page_size, search=search, is_active=True
    )


@router.get(
    "/admin/",
    response_model=PaginatedResponse[CategoryRead],
    summary="List all Categories",
)
async def list_all_categories(
    db_session: DbSession,
    page: int = Query(default=1, ge=1, description="Page number for pagination"),
    page_size: int = Query(
        default=10, ge=1, le=100, description="Number of categories per page"
    ),
    is_active: Optional[bool] = Query(
        default=None, description="Filter by active status"
    ),
    search: Optional[str] = Query(default="", description="Search categories by name"),
) -> PaginatedResponse[CategoryRead]:
    return await CategoryService.list_categories(
        db_session, page=page, page_size=page_size, search=search, is_active=is_active
    )


@router.get(
    "/{category_id}", response_model=CategoryRead, summary="Get Category Details"
)
async def get_category(
    db_session: DbSession,
    category_id: UUID,
):
    return await CategoryService.get_category(db_session, category_id)


@router.post(
    "/",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create New Category",
    dependencies=[role_checker_admin],
)
async def create_category(
    db_session: DbSession,
    category_data: CategoryCreate,
):
    return await CategoryService.create_category(db_session, category_data)


@router.patch(
    "/{category_id}",
    response_model=CategoryRead,
    summary="Update Category",
    dependencies=[role_checker_admin],
)
async def update_category(
    db_session: DbSession,
    category_id: UUID,
    update_data: CategoryUpdate,
):
    return await CategoryService.update_category(db_session, category_id, update_data)


@router.delete(
    "/{category_id}",
    dependencies=[role_checker_admin],
    summary="Delete Category",
)
async def delete_category(db_session: DbSession, category_id: UUID) -> JSONResponse:
    await CategoryService.delete_category(db_session, category_id)
    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content={"message": "Category deleted successfully"},
    )
