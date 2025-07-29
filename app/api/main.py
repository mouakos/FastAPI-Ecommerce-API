from fastapi import APIRouter
from app.api.routes.v1 import (
    accounts,
    auth,
    users,
    categories,
    products,
    tags,
    reviews,
    carts,
    wishlists,
)


api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(accounts.router)
api_router.include_router(carts.router)
api_router.include_router(users.router)
api_router.include_router(categories.router)
api_router.include_router(products.router)
api_router.include_router(tags.router)
api_router.include_router(reviews.router)
api_router.include_router(wishlists.router)
