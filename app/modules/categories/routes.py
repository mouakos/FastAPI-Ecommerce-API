from typing import Annotated, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database.core import get_session
from app.utils.paginate import PaginatedResponse
from app.modules.auth.dependencies import RoleChecker
from .service import CategoryService
from .schemas import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(prefix="/api/v1/categories", tags=["Categories"])

role_checker_admin = Depends(RoleChecker(["admin"]))

DbSession = Annotated[AsyncSession, Depends(get_session)]


@router.get("/", response_model=PaginatedResponse[CategoryRead])
async def list_active_categories(
    db: DbSession,
    page: int = Query(default=1, ge=1, description="Page number for pagination"),
    page_size: int = Query(
        default=10, ge=1, le=100, description="Number of categories per page"
    ),
    name: Optional[str] = Query(default="", description="Search categories by name"),
) -> PaginatedResponse[CategoryRead]:
    return await CategoryService.list_categories(
        db, page=page, page_size=page_size, name=name, is_active=True
    )


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(
    db: DbSession,
    category_id: UUID,
):
    return await CategoryService.get_category(db, category_id)


@router.get(
    "/all/",
    response_model=PaginatedResponse[CategoryRead],
    dependencies=[role_checker_admin],
)
async def list_all_categories(
    db: DbSession,
    page: int = Query(default=1, ge=1, description="Page number for pagination"),
    page_size: int = Query(
        default=10, ge=1, le=100, description="Number of categories per page"
    ),
    is_active: Optional[bool] = Query(
        default=None, description="Filter by active status"
    ),
    name: Optional[str] = Query(default="", description="Search categories by name"),
) -> PaginatedResponse[CategoryRead]:
    return await CategoryService.list_categories(
        db, page=page, page_size=page_size, name=name, is_active=is_active
    )


@router.post(
    "/",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[role_checker_admin],
)
async def create_category(
    db: DbSession,
    category_data: CategoryCreate,
):
    return await CategoryService.create_category(db, category_data)


@router.patch(
    "/{category_id}",
    response_model=CategoryRead,
    dependencies=[role_checker_admin],
)
async def update_category(
    db: DbSession,
    category_id: UUID,
    update_data: CategoryUpdate,
):
    return await CategoryService.update_category(db, category_id, update_data)


@router.delete(
    "/{category_id}",
    dependencies=[role_checker_admin],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_category(db: DbSession, category_id: UUID) -> None:
    await CategoryService.delete_category(db, category_id)
