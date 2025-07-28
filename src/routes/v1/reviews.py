from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from typing import Optional

from fastapi.responses import JSONResponse

from src.reviews.schemas import (
    AdminReviewUpdate,
    ReviewCreate,
    ReviewRead,
    ReviewUpdate,
)
from src.reviews.service import ReviewService
from src.core.dependencies import DbSession, CurrentUser, RoleChecker
from src.users.schemas import UserRole
from src.utils.paginate import PaginatedResponse


router = APIRouter(prefix="/api/v1/reviews", tags=["Reviews"])
admin_role_checker = Depends(RoleChecker([UserRole.admin]))


@router.get(
    "/product/{product_id}",
    response_model=PaginatedResponse[ReviewRead],
    summary="List reviews for a product",
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
    )


@router.post(
    "/product/{product_id}",
    response_model=ReviewRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add a review to a product",
)
async def create_review(
    product_id: UUID,
    data: ReviewCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> ReviewRead:
    return await ReviewService.create_review(db, data, current_user.id, product_id)


@router.patch(
    "/{review_id}",
    response_model=ReviewRead,
    summary="Update a review",
)
async def update_review(
    review_id: UUID,
    data: ReviewUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> ReviewRead:
    return await ReviewService.update_review(db, review_id, current_user.id, data)


@router.patch(
    "admin/{review_id}",
    response_model=ReviewRead,
    summary="Change review visibility",
    dependencies=[admin_role_checker],
)
async def change_review_visibility(
    review_id: UUID,
    data: AdminReviewUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> ReviewRead:
    return await ReviewService.change_review_visibility(
        db, review_id, current_user.id, data
    )


@router.get(
    "/{review_id}",
    response_model=ReviewRead,
    summary="Get review by ID",
)
async def get_review(
    review_id: UUID, db: DbSession, current_user: CurrentUser
) -> ReviewRead:
    return await ReviewService.get_review(db, review_id)


@router.delete("/{review_id}", summary="Delete a review")
async def delete_review(
    review_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> JSONResponse:
    await ReviewService.delete_review(db, review_id, current_user.id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Review deleted successfully"},
    )
