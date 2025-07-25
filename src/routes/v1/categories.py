from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from fastapi_pagination import Page
from src.categories.schemas import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
)
from src.core.dependencies import DbSession, RoleChecker
from src.categories.service import CategoryService
from src.users.schemas import UserRole


router = APIRouter(prefix="/api/v1/categories", tags=["Categories"])

role_checker_admin = Depends(RoleChecker([UserRole.admin]))


# --- Public Endpoints ---
@router.get("/", response_model=Page[CategoryRead], summary="List all Categories")
async def list_categories(
    db_session: DbSession,
    search: Optional[str] = Query("", description="Search categories by name"),
) -> Page[CategoryRead]:
    return await CategoryService.get_category_tree(db_session, search=search)


@router.get(
    "/{category_id}", response_model=CategoryRead, summary="Get Category Details"
)
async def get_category(
    db_session: DbSession,
    category_id: UUID,
):
    return await CategoryService.get_category(db_session, category_id)


# --- Admin Endpoints ---
@router.post(
    "/",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create New Category",
)
async def create_category(
    db_session: DbSession,
    category_data: CategoryCreate,
):
    return await CategoryService.create_category(db_session, category_data)


@router.put(
    "/{category_id}",
    response_model=CategoryRead,
    summary="Update Category",
)
async def update_category(
    db_session: DbSession,
    category_id: UUID,
    update_data: CategoryUpdate,
):
    return await CategoryService.update_category(db_session, category_id, update_data)


@router.delete(
    "/{category_id}",
    # dependencies=[role_checker_admin],
    summary="Delete Category",
)
async def delete_category(db_session: DbSession, category_id: UUID) -> JSONResponse:
    await CategoryService.delete_category(db_session, category_id)
    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content={"message": "Category deleted successfully"},
    )
