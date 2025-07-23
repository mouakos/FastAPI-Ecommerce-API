from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./ecommerce_dev.db"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SECRET_KEY: str = "your_secret_key"
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"


settings = Settings()
