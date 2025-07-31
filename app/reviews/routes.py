from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from typing import Optional, Annotated
from sqlmodel.ext.asyncio.session import AsyncSession



from app.reviews.schemas import (
    AdminReviewUpdate,
    ReviewCreate,
    ReviewRead,
    ReviewUpdate,
)
from app.auth.schemas import TokenData
from app.reviews.service import ReviewService
from app.auth.dependencies import  RoleChecker, AccessTokenBearer
from app.users.schemas import UserRole
from app.utils.paginate import PaginatedResponse
from app.database.core import get_session


router = APIRouter(prefix="/api/v1/reviews", tags=["Reviews"])
admin_role_checker = Depends(RoleChecker([UserRole.admin]))

DbSession = Annotated[AsyncSession, Depends(get_session)]
AccessToken = Annotated[TokenData, Depends(AccessTokenBearer())]

# User endpoints
@router.get(
    "/product/{product_id}",
    response_model=PaginatedResponse[ReviewRead],
    summary="List published product reviews",
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
    summary="Add a review to a product",
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
    summary="Update my review",
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
    summary="Get review by ID",
)
async def get_review(
    review_id: UUID, db: DbSession, token_data: AccessToken
) -> ReviewRead:
    return await ReviewService.get_review(db, review_id)


@router.delete(
    "/{review_id}", summary="Delete my review", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_review(
    review_id: UUID,
    db: DbSession,
    token_data: AccessToken,
) -> None:
    await ReviewService.delete_review(db, review_id, UUID(token_data.sub))


# Admin endpoints
@router.get(
    "/admin/product/{product_id}",
    response_model=PaginatedResponse[ReviewRead],
    summary="List all product reviews (admin)",
    dependencies=[admin_role_checker],
)
async def admin_list_all_product_reviews(
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
    "/admin/{review_id}",
    response_model=ReviewRead,
    summary="Change review visibility (admin)",
    dependencies=[admin_role_checker],
)
async def admin_change_review_visibility(
    review_id: UUID,
    data: AdminReviewUpdate,
    db: DbSession,
    token_data: AccessToken,
) -> ReviewRead:
    return await ReviewService.change_review_visibility(
        db, review_id, UUID(token_data.sub), data
    )


@router.delete(
    "/admin/{review_id}",
    summary="Delete any review (admin)",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[admin_role_checker],
)
async def admin_delete_review(
    review_id: UUID,
    db: DbSession,
    token_data: AccessToken,
) -> None:
    await ReviewService.delete_review(db, review_id, UUID(token_data.sub))
