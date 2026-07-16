from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_ENV: str = "development"
    SECRET_KEY: str = "change-me"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    DATABASE_URL: str = "postgresql://edgeflow:change-me@localhost:5432/edgeflow"
    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()