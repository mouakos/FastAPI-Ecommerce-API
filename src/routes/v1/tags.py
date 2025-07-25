from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from uuid import UUID

from src.core.dependencies import DbSession
from src.tags.schemas import TagCreate, TagRead, TagUpdate
from src.tags.service import TagService

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.get("/", response_model=list[TagRead], summary="List all tags")
async def list_tags(db: DbSession) -> list[TagRead]:
    return await TagService.list_tags(db)


@router.get("/{tag_id}", response_model=TagRead, summary="Get tag by ID")
async def get_tag(tag_id: UUID, db: DbSession) -> TagRead:
    return await TagService.get_tag(db, tag_id)


@router.post(
    "/",
    response_model=TagRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new tag",
)
async def create_tag(data: TagCreate, db: DbSession) -> TagRead:
    return await TagService.create_tag(db, data)


@router.patch("/{tag_id}", response_model=TagRead, summary="Update an existing tag")
async def update_tag(tag_id: UUID, data: TagUpdate, db: DbSession) -> TagRead:
    return await TagService.update_tag(db, tag_id, data)


@router.delete("/{tag_id}", summary="Delete a tag")
async def delete_tag(tag_id: UUID, db: DbSession) -> JSONResponse:
    await TagService.delete_tag(db, tag_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Tag deleted successfully"},
    )
