from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.routes.v1 import accounts, auth, users
from src.database.core import init_db
from src.core.logging import LogLevel, setup_logging
from src.core.exception_handler import register_all_errors

setup_logging(LogLevel.info)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize resources here if needed
    await init_db()
    yield
    # Cleanup resources here if needed


app = FastAPI(
    lifespan=lifespan,
    description="This is a simple e-commerce API built with FastAPI.",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
    title="E-commerce API",
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/license/mit/",
    },
    version="v1",
    contact={
        "name": "Stephane Mouako",
        "url": "https://github.com/mouakos",
    },
    openapi_tags=[
        {
            "name": "Auth",
            "description": "Operations related to user authentication.",
        },
        {
            "name": "Accounts",
            "description": "Operations related to user accounts.",
        },
        {
            "name": "Users",
            "description": "Operations related to user management.",
        },
    ],
    swagger_ui_parameters={
        "syntaxHighlight.theme": "monokai",
        "layout": "BaseLayout",
        "filter": True,
        "tryItOutEnabled": True,
        "onComplete": "Ok",
    },
)

# Register exception handlers
register_all_errors(app)

# Include routers
app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(users.router)
