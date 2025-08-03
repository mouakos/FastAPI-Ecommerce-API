from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_ACCESS_TOKEN_EXPIRE_SECONDS: int = 60
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str
    ADMIN_FULL_NAME: str

    model_config = SettingsConfigDict(
        env_file=".env",  # Load environment variables from .env file
        extra="ignore",  # Ignore extra fields not defined in the model
    )


settings = Settings()
