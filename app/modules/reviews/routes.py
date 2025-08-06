from fastapi import APIRouter, Depends, Query, status
from typing import Optional, Annotated
from sqlmodel.ext.asyncio.session import AsyncSession

from app.utils.paginate import PaginatedResponse
from app.database.core import get_session
from app.modules.auth.dependencies import RoleChecker, AccessToken
from .service import ReviewService
from .schemas import AdminReviewUpdate, ReviewCreate, ReviewRead, ReviewUpdate

router = APIRouter(prefix="/api/v1/products", tags=["Reviews"])
admin_role_checker = Depends(RoleChecker(["admin"]))

DbSession = Annotated[AsyncSession, Depends(get_session)]


@router.get("/{product_id}/reviews", response_model=PaginatedResponse[ReviewRead])
async def list_product_reviews(
    product_id: int,
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
    "/{product_id}/reviews",
    response_model=ReviewRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_product_review(
    product_id: int,
    data: ReviewCreate,
    db: DbSession,
    token_data: AccessToken,
) -> ReviewRead:
    return await ReviewService.create_product_review(
        db,
        token_data.get_int(),
        product_id,
        data,
    )


@router.get("/{product_id}/reviews/{review_id}", response_model=ReviewRead)
async def get_product_review(
    product_id: int, review_id: int, db: DbSession, _: AccessToken
) -> ReviewRead:
    return await ReviewService.get_product_review(db, product_id, review_id)


@router.patch("/{product_id}/reviews/{review_id}", response_model=ReviewRead)
async def update_product_review(
    product_id: int,
    review_id: int,
    data: ReviewUpdate,
    db: DbSession,
    token_data: AccessToken,
) -> ReviewRead:
    return await ReviewService.update_product_review(
        db, token_data.get_int(), product_id, review_id, data
    )


@router.delete(
    "/{product_id}/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_product_review(
    product_id: int,
    review_id: int,
    db: DbSession,
    token_data: AccessToken,
) -> None:
    await ReviewService.delete_product_review(
        db, token_data.get_int(), product_id, review_id
    )


@router.get(
    "/{product_id}/reviews/all",
    response_model=PaginatedResponse[ReviewRead],
    dependencies=[admin_role_checker],
)
async def list_all_product_reviews(
    product_id: int,
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
    "/{product_id}/reviews/{review_id}/update-visibility",
    response_model=ReviewRead,
    dependencies=[admin_role_checker],
)
async def change_review_visibility(
    product_id: int,
    review_id: int,
    data: AdminReviewUpdate,
    db: DbSession,
) -> ReviewRead:
    return await ReviewService.change_product_review_visibility(
        db, product_id, review_id, data
    )
