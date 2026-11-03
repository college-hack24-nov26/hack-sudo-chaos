import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory for the backend (where .env resides)
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables and .env file.
    Validates types and prevents credential leaks.
    """
    APP_NAME: str = "YumSure"
    APP_ENV: str = "development"
    API_V1_STR: str = "/api/v1"

    # Database URL format: postgresql+psycopg://username:password@localhost:5432/yumsure_db
    DATABASE_URL: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/yumsure_db",
        description="SQLAlchemy-compatible database connection string for PostgreSQL via Psycopg 3."
    )

    # Optional Connection Pool tuning
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800  # Recycle connections after 30 minutes to prevent stale sockets

    model_config = SettingsConfigDict(
        env_file=(str(BACKEND_DIR / ".env"), ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )

    def get_masked_database_url(self) -> str:
        """
        Returns a sanitized DATABASE_URL with the password masked for safe logging.
        Prevents credential leakage in log files or console output.
        """
        try:
            from urllib.parse import urlparse
            parsed = urlparse(self.DATABASE_URL)
            if parsed.password:
                sanitized_netloc = f"{parsed.username}:******@{parsed.hostname}"
                if parsed.port:
                    sanitized_netloc += f":{parsed.port}"
                return parsed._replace(netloc=sanitized_netloc).geturl()
            return self.DATABASE_URL
        except Exception:
            return "postgresql+psycopg://[credentials_masked]"


# Instantiate application settings singleton
settings = Settings()

