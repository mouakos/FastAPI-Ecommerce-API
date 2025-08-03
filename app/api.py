from fastapi import APIRouter
from app.modules.addresses.routes import router as addresses
from app.modules.auth.routes import router as auth
from app.modules.accounts.routes import router as accounts
from app.modules.carts.routes import router as carts
from app.modules.categories.routes import router as categories
from app.modules.products.routes import router as products
from app.modules.reviews.routes import router as reviews
from app.modules.tags.routes import router as tags
from app.modules.users.routes import router as users
from app.modules.wishlist.routes import router as wishlists
from app.modules.orders.routes import router as orders


api_router = APIRouter()
api_router.include_router(auth)
api_router.include_router(accounts)
api_router.include_router(users)
api_router.include_router(addresses)
api_router.include_router(carts)
api_router.include_router(categories)
api_router.include_router(products)
api_router.include_router(tags)
api_router.include_router(reviews)
api_router.include_router(wishlists)
api_router.include_router(orders)
