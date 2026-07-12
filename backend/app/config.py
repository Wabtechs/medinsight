from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "MedInsight API"
    APP_VERSION: str = "1.0.0"
    DATABASE_URL: str = "postgresql+asyncpg://medinsight:medinsight_secret@localhost:5432/medinsight"
    SYNC_DATABASE_URL: str = "postgresql+sync://medinsight:medinsight_secret@localhost:5432/medinsight"
    SECRET_KEY: str = "medinsight-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    RATE_LIMIT_PER_MINUTE: int = 60

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
