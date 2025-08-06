from typing import Annotated, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from app.utils.paginate import PaginatedResponse
from app.database.core import get_session
from app.modules.auth.dependencies import RoleChecker
from .schemas import TagAdd, TagCreate, TagRead, TagUpdate
from .service import TagService

router = APIRouter(prefix="/api/v1", tags=["Tags"])
role_checker_admin = Depends(RoleChecker(["admin"]))

DbSession = Annotated[AsyncSession, Depends(get_session)]


@router.get("/tags", response_model=PaginatedResponse[TagRead])
async def list_tags(
    db_session: DbSession,
    page: int = Query(default=1, ge=1, description="Page number for pagination"),
    page_size: int = Query(
        default=10, ge=1, le=100, description="Number of tags per page"
    ),
    name: Optional[str] = Query(default=None, description="Search tags by name"),
) -> PaginatedResponse[TagRead]:
    return await TagService.list_tags(db_session, page, page_size, name)


@router.get("/tags/{tag_id}", response_model=TagRead)
async def get_tag(tag_id: int, db_session: DbSession) -> TagRead:
    return await TagService.get_tag(db_session, tag_id)


@router.post(
    "/tags",
    response_model=TagRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[role_checker_admin],
)
async def create_tag(data: TagCreate, db_session: DbSession) -> TagRead:
    return await TagService.create_tag(db_session, data)


@router.patch(
    "/tags/{tag_id}",
    response_model=TagRead,
    dependencies=[role_checker_admin],
)
async def update_tag(tag_id: int, data: TagUpdate, db_session: DbSession) -> TagRead:
    return await TagService.update_tag(db_session, tag_id, data)


@router.delete(
    "/tags/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[role_checker_admin],
)
async def delete_tag(tag_id: int, db_session: DbSession) -> None:
    await TagService.delete_tag(db_session, tag_id)


@router.post(
    "/product/{product_id}/tags",
    dependencies=[role_checker_admin],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def add_tags_to_product(
    product_id: int, db_session: DbSession, tags: TagAdd
) -> None:
    await TagService.add_tags_to_product(db_session, product_id, tags)


@router.delete(
    "/product/{product_id}/tags/{tag_id}",
    dependencies=[role_checker_admin],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_tag_from_product(
    tag_id: int, product_id: int, db_session: DbSession
) -> None:
    await TagService.remove_tag_from_product(db_session, product_id, tag_id)
