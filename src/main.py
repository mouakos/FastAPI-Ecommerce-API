from fastapi import FastAPI

from .logging import LogLevel, setup_logging

setup_logging(LogLevel.info)

app = FastAPI(
    description="This is a simple e-commerce API built with FastAPI.",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
    title="E-commerce API",
    version="1.0.0",
    contact={
        "name": "Stephane Mouako",
        "url": "https://github.com/mouakos",
    },
    swagger_ui_parameters={
        "syntaxHighlight.theme": "monokai",
        "layout": "BaseLayout",
        "filter": True,
        "tryItOutEnabled": True,
        "onComplete": "Ok",
    },
)


@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI Ecommerce API"}
