from typing import Optional
from fastapi import APIRouter, Depends, status, Query
from fastapi.responses import JSONResponse
from uuid import UUID

from src.core.dependencies import DbSession, RoleChecker
from src.tags.schemas import TagCreate, TagRead, TagUpdate
from src.tags.service import TagService
from src.users.schemas import UserRole
from src.utils.paginate import PaginatedResponse

router = APIRouter(prefix="/tags", tags=["Tags"])

role_checker_admin = Depends(RoleChecker([UserRole.admin]))


@router.get("/", response_model=PaginatedResponse[TagRead], summary="List all tags")
async def list_tags(
    db_session: DbSession,
    page: int = Query(default=1, ge=1, description="Page number for pagination"),
    page_size: int = Query(
        default=10, ge=1, le=100, description="Number of tags per page"
    ),
    search: Optional[str] = Query(default="", description="Search tags by name"),
) -> PaginatedResponse[TagRead]:
    return await TagService.list_tags(db_session, page, page_size, search)


@router.get("/{tag_id}", response_model=TagRead, summary="Get tag by ID")
async def get_tag(tag_id: UUID, db_session: DbSession) -> TagRead:
    return await TagService.get_tag(db_session, tag_id)


@router.post(
    "/",
    response_model=TagRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new tag",
    dependencies=[role_checker_admin],
)
async def create_tag(data: TagCreate, db_session: DbSession) -> TagRead:
    return await TagService.create_tag(db_session, data)


@router.patch(
    "/{tag_id}",
    response_model=TagRead,
    summary="Update an existing tag",
    dependencies=[role_checker_admin],
)
async def update_tag(tag_id: UUID, data: TagUpdate, db_session: DbSession) -> TagRead:
    return await TagService.update_tag(db_session, tag_id, data)


@router.delete("/{tag_id}", summary="Delete a tag", dependencies=[role_checker_admin])
async def delete_tag(tag_id: UUID, db_session: DbSession) -> JSONResponse:
    await TagService.delete_tag(db_session, tag_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Tag deleted successfully"},
    )
