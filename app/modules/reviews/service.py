from math import ceil
from typing import Optional
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID

from app.models.product import Product
from app.models.review import Review
from app.exceptions import AuthorizationError, ConflictError, NotFoundError
from app.modules.products.service import ProductService
from app.modules.users.service import UserService
from app.utils.paginate import PaginatedResponse
from .schemas import AdminReviewUpdate, ReviewCreate, ReviewRead, ReviewUpdate


class ReviewService:
    @staticmethod
    async def create_product_review(
        db: AsyncSession,
        user_id: UUID,
        product_id: UUID,
        data: ReviewCreate,
    ) -> ReviewRead:
        """
        Create a new review for a product.

        Args:
            db (AsyncSession): The database session.
            data (ReviewCreate): Review data including rating and comment.
            user_id (UUID): ID of the user writing the review.

        Raises:
            NotFoundError: If the user or product does not exist.

        Returns:
            ReviewRead: The newly created review.
        """
        user = await UserService.get_user(db, user_id)

        product = await db.get(Product, product_id)
        if not product:
            raise NotFoundError(f"Product with ID {product_id} not found")

        stmt = select(Review).where(
            Review.user_id == user.id, Review.product_id == product.id
        )
        existing_review = (await db.exec(stmt)).first()

        if existing_review:
            raise ConflictError(
                f"Review by user {user.id} for product {product_id} already exists"
            )

        product.rating = await ReviewService._get_product_avg_rating(db, product)
        review = Review(
            rating=data.rating,
            comment=data.comment,
            product=product,
            user_id=user_id,
        )

        review = await db.add(review)
        await db.commit()
        return review

    @staticmethod
    async def get_product_review(
        db: AsyncSession, product_id: UUID, review_id: UUID
    ) -> ReviewRead:
        """
        Retrieve a review by its ID for a specific product.

        Args:
            db (AsyncSession): The database session.
            product_id (UUID): Product ID.
            review_id (UUID): Review ID.

        Raises:
            NotFoundError: If the product or review does not exist.

        Returns:
            ReviewRead: The requested review.
        """
        product = await ProductService.get_product(db, product_id)
        stmt = select(Review).where(
            Review.id == review_id, Review.product_id == product.id
        )
        review = (await db.exec(stmt)).first()
        if not review:
            raise NotFoundError(
                f"Review with ID {review_id} for product {product_id} not found"
            )

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
        ).order_by(Review.rating.desc())
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
    async def update_product_review(
        db: AsyncSession,
        user_id: UUID,
        product_id: UUID,
        review_id: UUID,
        data: ReviewUpdate,
    ) -> ReviewRead:
        """
        Update an existing review for a product.

        Args:
            db (AsyncSession): The database session.
            user_id (UUID): User ID.
            product_id (UUID): Product ID.
            review_id (UUID): Review ID.
            data (ReviewUpdate): Updated review data.

        Raises:
            NotFoundError: If the user, product, or review does not exist.
            AuthorizationError: If the user does not have permission to update the review.

        Returns:
            ReviewRead: The updated review.
        """
        user = await UserService.get_user(db, user_id)
        product = await ProductService.get_product(db, product_id)
        stmt = select(Review).where(
            Review.id == review_id,
            Review.user_id == user.id,
            Review.product_id == product.id,
        )
        review = (await db.exec(stmt)).first()
        if not review:
            raise NotFoundError(
                f"Review with ID {review_id} not found for product {product_id}"
            )

        if review.user_id != user.id:
            raise AuthorizationError(
                "You do not have permission to update this review."
            )

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(review, key, value)

        await db.commit()
        await ReviewService._update_product_avg_rating(db, product_id)
        return review

    @staticmethod
    async def change_product_review_visibility(
        db: AsyncSession,
        user_id: UUID,
        product_id: UUID,
        review_id: UUID,
        data: AdminReviewUpdate,
    ) -> ReviewRead:
        """
        Change the visibility of a review for a product.

        Args:
            db (AsyncSession): The database session.
            user_id (UUID): User ID of the admin.
            product_id (UUID): Product ID.
            review_id (UUID): Review ID.
            data (AdminReviewUpdate): Updated visibility data.

        Raises:
            NotFoundError: If the user, product, or review does not exist.

        Returns:
            ReviewRead: The updated review with new visibility status.
        """
        user = await UserService.get_user(db, user_id)

        product = await ProductService.get_product(db, product_id)

        stmt = select(Review).where(
            Review.user_id == user.id,
            Review.product_id == product.id,
        )
        review = (await db.exec(stmt)).first()
        if not review:
            raise NotFoundError(
                f"Review with ID {review_id} not found for product {product_id}"
            )

        if review.is_published != data.is_published:
            review.is_published = data.is_published
            await db.commit()

        return review

    @staticmethod
    async def delete_product_review(
        db: AsyncSession,
        user_id: UUID,
        product_id: UUID,
        review_id: UUID,
    ) -> None:
        """
        Delete a review by its ID.

        Args:
            db (AsyncSession): The database session.
            review_id (UUID): Review ID.

        Raises:
            NotFoundError: If the user, product, or review does not exist.
            AuthorizationError: If the user does not have permission to delete the review.
        """
        user = await UserService.get_user(db, user_id)
        product = await ProductService.get_product(db, product_id)
        stmt = select(Review).where(
            Review.user_id == user.id,
            Review.product_id == product.id,
        )
        review = (await db.exec(stmt)).first()
        if not review:
            raise NotFoundError(
                f"Review with ID {review_id} not found for product {product_id}"
            )

        if review.user_id != user.id and user.role != "admin":
            raise AuthorizationError(
                "You do not have permission to delete this review."
            )

        await db.delete(review)
        await db.commit()
        await ReviewService._update_product_avg_rating(db, product_id)

    @staticmethod
    async def _update_product_avg_rating(db: AsyncSession, product_id: UUID) -> None:
        """
        Update the average rating of a product after a review is deleted.

        Args:
            db (AsyncSession): The database session.
            product_id (UUID): Product ID.
            old_rating (float): The rating to be removed from the average.
        Raises:
            NotFoundError: If the product does not exist.

        Returns:
            None
        """
        stmt = select(Review).where(Review.product_id == product_id)
        reviews = (await db.exec(stmt)).all()

        product = await db.get(Product, product_id)
        if not product:
            raise NotFoundError(f"Product with ID {product_id} not found")

        if not reviews:
            product.rating = 0.0
            return

        total_rating = sum(review.rating for review in reviews if review.is_published)
        count = len([review for review in reviews if review.is_published])

        if count == 0:
            product.rating = 0.0
        else:
            product.rating = total_rating / count

        await db.commit()
