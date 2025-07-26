from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID

from src.models.review import Review
from src.models.product import Product
from src.models.user import User
from src.reviews.schemas import ReviewCreate, ReviewRead
from src.core.exceptions import (
    InsufficientPermission,
    ProductNotFound,
    ReviewNotFound,
    UserNotFound,
)


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
    async def list_reviews_for_product(
        db: AsyncSession, product_id: UUID
    ) -> list[ReviewRead]:
        """
        List all reviews for a specific product.

        Args:
            db (AsyncSession): The database session.
            product_id (UUID): Product ID.

        Returns:
            list[ReviewRead]: A list of reviews.
        """
        result = await db.exec(select(Review).where(Review.product_id == product_id))

        return [ReviewRead(**r.model_dump()) for r in result.all()]

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

        if review.user_id != user_id:
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
