from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from typing import Optional, Annotated
from sqlmodel.ext.asyncio.session import AsyncSession

from app.exceptions import AuthorizationError
from app.utils.paginate import PaginatedResponse
from app.database.core import get_session
from app.modules.auth.dependencies import RoleChecker, AccessToken
from .service import ReviewService
from .schemas import AdminReviewUpdate, ReviewCreate, ReviewRead, ReviewUpdate

router = APIRouter(prefix="/api/v1/reviews", tags=["Reviews"])
admin_role_checker = Depends(RoleChecker(["admin"]))

DbSession = Annotated[AsyncSession, Depends(get_session)]


@router.get(
    "/product/{product_id}",
    response_model=PaginatedResponse[ReviewRead],
)
async def list_product_reviews(
    product_id: UUID,
    db: DbSession,
    page: int = Query(default=1, ge=1, description="Page number for pagination"),
    page_size: int = Query(
        default=10, ge=1, le=100, description="Number of reviews per page"
    ),
    min_rating: Optional[int] = Query(
        default=None,
        ge=1,
        le=5,
        description="Filter reviews by minimum rating (1 to 5)",
    ),
    max_rating: Optional[int] = Query(
        default=None,
        ge=1,
        le=5,
        description="Filter reviews by maximum rating (1 to 5)",
    ),
) -> PaginatedResponse[ReviewRead]:
    return await ReviewService.list_product_reviews(
        db,
        product_id,
        page=page,
        size=page_size,
        min_rating=min_rating,
        max_rating=max_rating,
        is_published=True,
    )


@router.post(
    "/product/{product_id}",
    response_model=ReviewRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_review(
    product_id: UUID,
    data: ReviewCreate,
    db: DbSession,
    token_data: AccessToken,
) -> ReviewRead:
    return await ReviewService.create_review(db, data, UUID(token_data.sub), product_id)


@router.patch(
    "/{review_id}",
    response_model=ReviewRead,
)
async def update_review(
    review_id: UUID,
    data: ReviewUpdate,
    db: DbSession,
    token_data: AccessToken,
) -> ReviewRead:
    return await ReviewService.update_review(db, review_id, UUID(token_data.sub), data)


@router.get(
    "/{review_id}",
    response_model=ReviewRead,
)
async def get_review(
    review_id: UUID, db: DbSession, _: AccessToken
) -> ReviewRead:
    return await ReviewService.get_review(db, review_id)


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: UUID,
    db: DbSession,
    token_data: AccessToken,
) -> None:
    review = await ReviewService.get_review(db, review_id)
    if review.user_id != UUID(token_data.sub) or token_data.role != "admin":
        raise AuthorizationError("You do not have permission to delete this review.")
    await ReviewService.delete_review(db, review_id, UUID(token_data.sub))


@router.get(
    "/all/products/{product_id}",
    response_model=PaginatedResponse[ReviewRead],
    dependencies=[admin_role_checker],
)
async def list_all_product_reviews(
    product_id: UUID,
    db: DbSession,
    page: int = Query(default=1, ge=1, description="Page number for pagination"),
    page_size: int = Query(
        default=10, ge=1, le=100, description="Number of reviews per page"
    ),
    min_rating: Optional[int] = Query(
        default=None,
        ge=1,
        le=5,
        description="Filter reviews by minimum rating (1 to 5)",
    ),
    max_rating: Optional[int] = Query(
        default=None,
        ge=1,
        le=5,
        description="Filter reviews by maximum rating (1 to 5)",
    ),
    is_published: Optional[bool] = Query(
        default=None,
        description="Filter reviews by publication status",
    ),
) -> PaginatedResponse[ReviewRead]:
    return await ReviewService.list_product_reviews(
        db,
        product_id,
        page=page,
        size=page_size,
        min_rating=min_rating,
        max_rating=max_rating,
        is_published=is_published,
    )


@router.patch(
    "/{review_id}/change-visibility",
    response_model=ReviewRead,
    dependencies=[admin_role_checker],
)
async def change_review_visibility(
    review_id: UUID,
    data: AdminReviewUpdate,
    db: DbSession,
) -> ReviewRead:
    return await ReviewService.change_review_visibility(db, review_id, data)
