from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_ACCESS_TOKEN_EXPIRE_SECONDS: int = 60
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str
    ADMIN_FULL_NAME: str

    class Config:
        env_file = ".env"


settings = Settings()
