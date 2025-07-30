from typing import Optional
from fastapi import APIRouter, Depends, status, Query, HTTPException
from uuid import UUID

from app.dependencies import DbSession, RoleChecker
from app.tags.schemas import TagCreate, TagRead, TagReadDetail, TagUpdate
from app.tags.service import TagService
from app.users.schemas import UserRole
from app.utils.paginate import PaginatedResponse

router = APIRouter(prefix="/api/v1/tags", tags=["Tags"])
role_checker_admin = Depends(RoleChecker([UserRole.admin]))


# User endpoints
@router.get(
    "/",
    response_model=PaginatedResponse[TagRead],
    summary="List active tags",
)
async def list_tags(
    db_session: DbSession,
    page: int = Query(default=1, ge=1, description="Page number for pagination"),
    page_size: int = Query(
        default=10, ge=1, le=100, description="Number of tags per page"
    ),
    search: Optional[str] = Query(default="", description="Search tags by name"),
) -> PaginatedResponse[TagRead]:
    return await TagService.list_tags(
        db_session, page, page_size, search, is_active=True
    )


@router.get(
    "/{tag_id}",
    response_model=TagReadDetail,
    summary="Get tag by ID",
)
async def get_tag(tag_id: UUID, db_session: DbSession) -> TagReadDetail:
    tag = await TagService.get_tag(db_session, tag_id)
    if not tag.is_active:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


# Admin endpoints
@router.get(
    "/admin/",
    response_model=PaginatedResponse[TagRead],
    summary="List all tags (admin)",
    dependencies=[role_checker_admin],
)
async def admin_list_all_tags(
    db_session: DbSession,
    page: int = Query(default=1, ge=1, description="Page number for pagination"),
    page_size: int = Query(
        default=10, ge=1, le=100, description="Number of tags per page"
    ),
    search: Optional[str] = Query(default="", description="Search tags by name"),
    is_active: Optional[bool] = Query(
        default=None, description="Filter tags by active status"
    ),
) -> PaginatedResponse[TagRead]:
    return await TagService.list_tags(
        db_session, page=page, page_size=page_size, search=search, is_active=is_active
    )


@router.post(
    "/admin/",
    response_model=TagRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new tag (admin)",
    dependencies=[role_checker_admin],
)
async def admin_create_tag(data: TagCreate, db_session: DbSession) -> TagRead:
    return await TagService.create_tag(db_session, data)


@router.patch(
    "/admin/{tag_id}",
    response_model=TagRead,
    summary="Update an existing tag (admin)",
    dependencies=[role_checker_admin],
)
async def admin_update_tag(
    tag_id: UUID, data: TagUpdate, db_session: DbSession
) -> TagRead:
    return await TagService.update_tag(db_session, tag_id, data)


@router.delete(
    "/admin/{tag_id}",
    summary="Delete a tag (admin)",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[role_checker_admin],
)
async def admin_delete_tag(tag_id: UUID, db_session: DbSession) -> None:
    await TagService.delete_tag(db_session, tag_id)
