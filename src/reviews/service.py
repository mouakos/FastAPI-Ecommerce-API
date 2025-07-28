from datetime import datetime
from math import ceil
from typing import Optional
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID

from src.models.review import Review
from src.models.product import Product
from src.models.user import User, UserRole
from src.reviews.schemas import (
    AdminReviewUpdate,
    ReviewCreate,
    ReviewRead,
    ReviewUpdate,
)
from src.core.exceptions import (
    InsufficientPermission,
    ProductNotFound,
    ReviewAlreadyExists,
    ReviewNotFound,
    UserNotFound,
)
from src.utils.paginate import PaginatedResponse


class ReviewService:
    @staticmethod
    async def create_review(
        db: AsyncSession, data: ReviewCreate, user_id: UUID, product_id: UUID
    ) -> ReviewRead:
        """
        Create a new review for a product.

        Args:
            db (AsyncSession): The database session.
            data (ReviewCreate): Review data including rating and comment.
            user_id (UUID): ID of the user writing the review.

        Raises:
            ProductNotFound: If the product does not exist.
            UserNotFound: If the user does not exist.

        Returns:
            ReviewRead: The newly created review.
        """
        user = await db.get(User, user_id)
        if not user:
            raise UserNotFound()

        product = await db.get(Product, product_id)
        if not product:
            raise ProductNotFound()

        existing_review = await db.exec(
            select(Review).where(
                Review.product_id == product_id, Review.user_id == user_id
            )
        )

        if existing_review.first():
            raise ReviewAlreadyExists()

        review = Review(
            rating=data.rating,
            comment=data.comment,
            product_id=product_id,
            user_id=user_id,
        )

        db.add(review)
        await db.commit()
        await db.refresh(review)

        # Update product rating after adding a new review
        await ReviewService._update_product_rating(db, product_id)

        return ReviewRead(**review.model_dump())

    @staticmethod
    async def get_review(db: AsyncSession, review_id: UUID) -> ReviewRead:
        """
        Retrieve a review by its ID.

        Args:
            db (AsyncSession): The database session.
            review_id (UUID): Review ID.

        Raises:
            ReviewNotFound: If no review is found with the given ID.

        Returns:
            ReviewRead: The requested review.
        """
        review = await db.get(Review, review_id)
        if not review:
            raise ReviewNotFound()
        return ReviewRead(**review.model_dump())

    @staticmethod
    async def list_product_reviews(
        db_session: AsyncSession,
        product_id: UUID,
        page: int,
        size: int,
        min_rating: Optional[int] = None,
        max_rating: Optional[int] = None,
        is_published: Optional[bool] = None,
    ) -> PaginatedResponse[ReviewRead]:
        """
        List reviews for a specific product with pagination and optional rating filter.

        Args:
            db (AsyncSession): The database session.
            product_id (UUID): Product ID.
            page (int): Page number for pagination.
            size (int): Number of reviews per page.
            min_rating (Optional[int]): Minimum rating to filter reviews.
            max_rating (Optional[int]): Maximum rating to filter reviews.

        Returns:
            PaginatedResponse[ReviewRead]: A paginated response containing review data.
        """
        # Get total count (without limit/offset)
        count_stmt = (
            select(func.count())
            .select_from(Review)
            .where(
                Review.product_id == product_id,
                func.between(
                    Review.rating,
                    min_rating if min_rating else 1,
                    max_rating if max_rating else 5,
                ),
                (Review.is_published == is_published)
                if is_published is not None
                else True,
            )
        )
        total = (await db_session.exec(count_stmt)).one()

        # Get paginated reviews
        result = await db_session.exec(
            select(Review)
            .where(
                Review.product_id == product_id,
                func.between(
                    Review.rating,
                    min_rating if min_rating else 1,
                    max_rating if max_rating else 5,
                ),
                (Review.is_published == is_published)
                if is_published is not None
                else True,
            )
            .order_by(Review.created_at.desc())
            .limit(size)
            .offset((page - 1) * size)
        )
        reviews = result.all()

        return PaginatedResponse[ReviewRead](
            total=total,
            page=page,
            size=size,
            pages=ceil(total / size) if total else 1,
            items=[ReviewRead(**review.model_dump()) for review in reviews],
        )

    @staticmethod
    async def update_review(
        db: AsyncSession, review_id: UUID, user_id: UUID, data: ReviewUpdate
    ) -> ReviewRead:
        """
        Update an existing review.

        Args:
            db (AsyncSession): The database session.
            review_id (UUID): Review ID.
            user_id (UUID): ID of the user updating the review.
            data (ReviewUpdate): Updated review data.

        Raises:
            ReviewNotFound: If the review does not exist.
            InsufficientPermission: If the user does not own the review.

        Returns:
            ReviewRead: The updated review.
        """
        user = await db.get(User, user_id)
        if not user:
            raise UserNotFound()

        review = await db.get(Review, review_id)
        if not review:
            raise ReviewNotFound()

        if review.user_id != user_id:
            raise InsufficientPermission()

        review.rating = data.rating if data.rating is not None else review.rating
        review.comment = data.comment if data.comment is not None else review.comment
        review.updated_at = datetime.utcnow()

        db.add(review)
        await db.commit()
        await db.refresh(review)

        # Update product rating after updating a review
        await ReviewService._update_product_rating(db, review.product_id)

        return ReviewRead(**review.model_dump())

    @staticmethod
    async def change_review_visibility(
        db: AsyncSession, review_id: UUID, data: AdminReviewUpdate
    ) -> ReviewRead:
        """
        Change the visibility of a review.

        Args:
            db (AsyncSession): The database session.
            review_id (UUID): Review ID.
            data (AdminReviewUpdate): Updated visibility data.

        Raises:
            ReviewNotFound: If the review does not exist.

        Returns:
            ReviewRead: The updated review with new visibility status.
        """
        review = await db.get(Review, review_id)
        if not review:
            raise ReviewNotFound()

        review.is_published = data.is_published
        review.updated_at = datetime.utcnow()

        db.add(review)
        await db.commit()
        await db.refresh(review)

        return ReviewRead(**review.model_dump())

    @staticmethod
    async def delete_review(db: AsyncSession, review_id: UUID, user_id: UUID) -> None:
        """
        Delete a review by its ID.

        Args:
            db (AsyncSession): The database session.
            review_id (UUID): Review ID.
            user_id (UUID): ID of the user requesting the deletion.

        Raises:
            ReviewNotFound: If the review does not exist or does not belong to the user.
        """
        user = await db.get(User, user_id)
        if not user:
            raise UserNotFound()
        review = await db.get(Review, review_id)
        if not review:
            raise ReviewNotFound()

        if review.user_id != user_id and user.role != UserRole.admin:
            raise InsufficientPermission()

        await db.delete(review)
        await db.commit()

        # Update product rating after deleting a review
        await ReviewService._update_product_rating(db, review.product_id)

    @staticmethod
    async def _update_product_rating(db: AsyncSession, product_id: UUID) -> None:
        """
        Update the product's rating based on its reviews.
        Args:
            db (AsyncSession): The database session.
            product_id (UUID): Product ID.
        """

        result = await db.exec(
            select(func.avg(Review.rating)).where(Review.product_id == product_id)
        )
        avg_rating = result.first() or 0.0

        product = await db.get(Product, product_id)
        product.rating = round(avg_rating, 2)
        db.add(product)
        await db.commit()
        await db.refresh(product)
