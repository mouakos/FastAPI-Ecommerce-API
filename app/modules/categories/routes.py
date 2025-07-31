from typing import Annotated, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from ...database.core import get_session
from ...utils.paginate import PaginatedResponse
from ..auth.dependencies import RoleChecker
from .service import CategoryService
from .schemas import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(prefix="/api/v1/categories", tags=["Categories"])

role_checker_admin = Depends(RoleChecker(["admin"]))

DbSession = Annotated[AsyncSession, Depends(get_session)]


# User endpoints
@router.get(
    "/",
    response_model=PaginatedResponse[CategoryRead],
    summary="List active categories",
)
async def list_active_categories(
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
    "/{category_id}", response_model=CategoryRead, summary="Get category details"
)
async def get_category(
    db_session: DbSession,
    category_id: UUID,
):
    category = await CategoryService.get_category(db_session, category_id)
    if not category.is_active:
        # Hide inactive categories from normal users
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Category not found")
    return category


# Admin endpoints
@router.get(
    "/admin/",
    response_model=PaginatedResponse[CategoryRead],
    summary="List all categories (admin)",
    dependencies=[role_checker_admin],
)
async def admin_list_all_categories(
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
    "/admin/{category_id}",
    response_model=CategoryRead,
    summary="Get category details (admin)",
    dependencies=[role_checker_admin],
)
async def admin_get_category(
    db_session: DbSession,
    category_id: UUID,
):
    return await CategoryService.get_category(db_session, category_id)


@router.post(
    "/admin/",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create new category (admin)",
    dependencies=[role_checker_admin],
)
async def admin_create_category(
    db_session: DbSession,
    category_data: CategoryCreate,
):
    return await CategoryService.create_category(db_session, category_data)


@router.patch(
    "/admin/{category_id}",
    response_model=CategoryRead,
    summary="Update category (admin)",
    dependencies=[role_checker_admin],
)
async def admin_update_category(
    db_session: DbSession,
    category_id: UUID,
    update_data: CategoryUpdate,
):
    return await CategoryService.update_category(db_session, category_id, update_data)


@router.delete(
    "/admin/{category_id}",
    dependencies=[role_checker_admin],
    summary="Delete category (admin)",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def admin_delete_category(db_session: DbSession, category_id: UUID) -> None:
    await CategoryService.delete_category(db_session, category_id)
