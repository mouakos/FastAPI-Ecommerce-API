from math import ceil
from typing import Optional
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID

from app.models.product import Product
from app.models.review import Review
from app.models.user import User

from app.reviews.schemas import (
    AdminReviewUpdate,
    ReviewCreate,
    ReviewRead,
    ReviewUpdate,
)
from app.exceptions import (
    AuthorizationError,
    ConflictError,
    NotFoundError,
)
from app.users.schemas import UserRole
from app.utils.paginate import PaginatedResponse


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
            ResourceNotFoundError: If the user or product does not exist.

        Returns:
            ReviewRead: The newly created review.
        """
        user = await db.get(User, user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")

        product = await db.get(Product, product_id)
        if not product:
            raise NotFoundError(f"Product with ID {product_id} not found")

        stmt = select(Review).where(
            Review.user_id == user_id, Review.product_id == product_id
        )
        existing_review = (await db.exec(stmt)).first()

        if existing_review:
            raise ConflictError(
                f"Review by user {user_id} for product {product_id} already exists"
            )

        review = Review(
            rating=data.rating,
            comment=data.comment,
            product_id=product_id,
            user_id=user_id,
        )

        review = await db.add(review)
        await db.commit()

        # Update product rating after adding a new review
        await ReviewService.update_product_avg_rating(db, product)

        return review

    @staticmethod
    async def get_review(db: AsyncSession, review_id: UUID) -> ReviewRead:
        """
        Retrieve a review by its ID.

        Args:
            db (AsyncSession): The database session.
            review_id (UUID): Review ID.

        Raises:
            ResourceNotFoundError: If no review is found with the given ID.

        Returns:
            ReviewRead: The requested review.
        """
        review = await db.get(Review, review_id)
        if not review:
            raise NotFoundError(f"Review with ID {review_id} not found")
        return review

    @staticmethod
    async def list_product_reviews(
        db: AsyncSession,
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

        # Get total count
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
        total = (await db.exec(count_stmt)).one()

        # Get paginated reviews
        result = await db.exec(
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

        return PaginatedResponse[Review](
            total=total,
            page=page,
            size=size,
            pages=ceil(total / size) if total else 1,
            items=reviews,
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
            NotFoundError: If the review or user does not exist.
            AuthorizationError: If the user does not own the review.

        Returns:
            ReviewRead: The updated review.
        """
        user = await db.get(User, user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")

        review = await db.get(Review, review_id)
        if not review:
            raise NotFoundError(f"Review with ID {review_id} not found")

        if review.user_id != user.id:
            raise AuthorizationError("You do not have permission to update this review")

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(review, key, value)

        db.add(review)
        await db.commit()

        # Update product rating after updating a review
        await ReviewService.update_product_avg_rating(db, review.product)

        return review

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
            NotFoundError: If the user review does not exist.

        Returns:
            ReviewRead: The updated review with new visibility status.
        """
        review = await db.get(Review, review_id)
        if not review:
            raise NotFoundError(f"Review with ID {review_id} not found")

        review.is_published = data.is_published

        db.add(review)
        await db.commit()

        return review

    @staticmethod
    async def delete_review(db: AsyncSession, review_id: UUID, user_id: UUID) -> None:
        """
        Delete a review by its ID.

        Args:
            db (AsyncSession): The database session.
            review_id (UUID): Review ID.
            user_id (UUID): ID of the user requesting the deletion.

        Raises:
            NotFoundError: If the user or review does not exist.
            AuthorizationError: If the user does not own the review or is not an admin.
        """
        user = await db.get(User, user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")

        review = await db.get(Review, review_id)
        if not review:
            raise NotFoundError(f"Review with ID {review_id} not found")

        if review.user_id != user.id and user.role != UserRole.admin:
            raise AuthorizationError("You do not have permission to delete this review")

        await db.delete(review)
        await db.commit()

        # Update product rating after deleting a review
        await ReviewService.update_product_avg_rating(db, review.product)

    @staticmethod
    async def update_product_avg_rating(db: AsyncSession, product: Product) -> float:
        """
        Update the average rating of a product based on its reviews.
        Args:
            db (AsyncSession): The database session.
            product (Product): The product to update.
        Returns:
            float: The new average rating.
        """
        result = await db.exec(
            select(func.avg(Review.rating)).where(Review.product_id == product.id)
        )

        avg_rating = result.first() or 0.0
        product.rating = round(avg_rating, 2)
        db.add(product)
        await db.commit()
