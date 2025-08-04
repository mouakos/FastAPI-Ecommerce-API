from typing import Annotated, Optional
from fastapi import APIRouter, Depends, status, Query, HTTPException
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession

from app.utils.paginate import PaginatedResponse
from app.database.core import get_session
from app.modules.auth.dependencies import RoleChecker
from .schemas import TagCreate, TagRead, TagReadDetail, TagUpdate
from .service import TagService

router = APIRouter(prefix="/api/v1/tags", tags=["Tags"])
role_checker_admin = Depends(RoleChecker(["admin"]))

DbSession = Annotated[AsyncSession, Depends(get_session)]


@router.get("/", response_model=PaginatedResponse[TagRead])
async def list_tags(
    db_session: DbSession,
    page: int = Query(default=1, ge=1, description="Page number for pagination"),
    page_size: int = Query(
        default=10, ge=1, le=100, description="Number of tags per page"
    ),
    name: Optional[str] = Query(default=None, description="Search tags by name"),
) -> PaginatedResponse[TagRead]:
    return await TagService.list_tags(db_session, page, page_size, name)


@router.get("/{tag_id}", response_model=TagReadDetail)
async def get_tag(tag_id: UUID, db_session: DbSession) -> TagReadDetail:
    tag = await TagService.get_tag(db_session, tag_id)
    if not tag.is_active:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.post(
    "/",
    response_model=TagRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[role_checker_admin],
)
async def admin_create_tag(data: TagCreate, db_session: DbSession) -> TagRead:
    return await TagService.create_tag(db_session, data)


@router.patch(
    "/{tag_id}",
    response_model=TagRead,
    dependencies=[role_checker_admin],
)
async def update_tag(tag_id: UUID, data: TagUpdate, db_session: DbSession) -> TagRead:
    return await TagService.update_tag(db_session, tag_id, data)

@router.delete(
    "/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[role_checker_admin],
)
async def admin_delete_tag(tag_id: UUID, db_session: DbSession) -> None:
    await TagService.delete_tag(db_session, tag_id)

# assign tag to a product
@router.post("/{tag_id}/assign", status_code=status.HTTP_204_NO_CONTENT)
async def add_tag_to_product(
    tag_id: UUID, product_id: UUID, db_session: DbSession
) -> None:
    await TagService.add_tag_to_product(db_session, tag_id, product_id)
    
# unassign tag from a product
@router.post("/{tag_id}/unassign", status_code=status.HTTP_204_NO_CONTENT)
async def remove_tag_from_product(
    tag_id: UUID, product_id: UUID, db_session: DbSession
) -> None:
    await TagService.remove_tag_from_product(db_session, tag_id, product_id)