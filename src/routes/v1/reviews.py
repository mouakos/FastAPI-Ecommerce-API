from uuid import UUID
from fastapi import APIRouter, Depends, status
from typing import List

from fastapi.responses import JSONResponse

from src.users.schemas import UserRole
from src.reviews.schemas import ReviewCreate, ReviewRead
from src.reviews.service import ReviewService
from src.core.dependencies import DbSession, CurrentUser, RoleChecker


router = APIRouter(prefix="/api/v1/reviews", tags=["Reviews"])

user_role_checker = Depends(RoleChecker([UserRole.admin, UserRole.customer]))
admin_role_checker = Depends(RoleChecker([UserRole.admin]))


@router.post(
    "/product/{product_id}",
    response_model=ReviewRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add a review to a product",
)
async def add_review_to_product(
    product_id: UUID,
    data: ReviewCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> ReviewRead:
    return await ReviewService.create_review(db, data, current_user.id, product_id)


@router.get(
    "/{review_id}",
    response_model=ReviewRead,
    summary="Get review by ID",
    dependencies=[user_role_checker],
)
async def get_review(review_id: UUID, db: DbSession) -> ReviewRead:
    return await ReviewService.get_review(db, review_id)


@router.get(
    "/product/{product_id}",
    response_model=List[ReviewRead],
    summary="List reviews for a product",
    dependencies=[admin_role_checker],
)
async def list_reviews_for_product(product_id: UUID, db: DbSession) -> List[ReviewRead]:
    return await ReviewService.list_reviews_for_product(db, product_id)


@router.delete(
    "/{review_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a review"
)
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
