import os
from pathlib import Path
from typing import Optional
from urllib.parse import urlsplit, urlunsplit, parse_qs, urlencode
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory for the backend (where .env resides)
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent


def normalize_pg_url(url: Optional[str], enforce_ssl_for_supabase: bool = True) -> Optional[str]:
    """
    Normalizes PostgreSQL connection URLs:
    - Automatically maps 'postgresql://' or 'postgres://' to SQLAlchemy Psycopg 3 dialect 'postgresql+psycopg://'.
    - Automatically enforces 'sslmode=require' for remote Supabase connections.
    - Preserves URL-encoded credentials (e.g. %40 for @ in passwords).
    - Preserves local PostgreSQL connection format without forcing SSL.
    """
    if not url:
        return None
    clean = str(url).strip().strip("'").strip('"')
    if clean.startswith("postgresql://"):
        clean = "postgresql+psycopg://" + clean[len("postgresql://"):]
    elif clean.startswith("postgres://"):
        clean = "postgresql+psycopg://" + clean[len("postgres://"):]

    # Enforce SSL for remote Supabase endpoints
    if enforce_ssl_for_supabase and ("supabase.co" in clean or "supabase.com" in clean):
        parsed = urlsplit(clean)
        query_dict = parse_qs(parsed.query)
        if "sslmode" not in query_dict:
            query_dict["sslmode"] = ["require"]
            new_query = urlencode(query_dict, doseq=True)
            clean = urlunsplit(parsed._replace(query=new_query))
    return clean


def mask_connection_url(url: Optional[str]) -> str:
    """
    Safely sanitizes connection strings for logs, telemetry, and CLI display.
    Never exposes plain-text or URL-encoded passwords.
    """
    if not url:
        return ""
    try:
        parsed = urlsplit(url)
        if "@" in parsed.netloc:
            userinfo, hostport = parsed.netloc.rsplit("@", 1)
            if ":" in userinfo:
                user = userinfo.split(":", 1)[0]
                masked_netloc = f"{user}:******@{hostport}"
            else:
                masked_netloc = f"{userinfo}@{hostport}"
            return urlunsplit(parsed._replace(netloc=masked_netloc))
        return url
    except Exception:
        return "postgresql+psycopg://[credentials_masked]"


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables and .env file.
    Validates types, enforces Psycopg 3 dialect, and protects credentials.
    """
    APP_NAME: str = "YumSure"
    APP_ENV: str = "development"
    API_V1_STR: str = "/api/v1"

    # Application Database Connection (Supabase shared dev or local fallback)
    DATABASE_URL: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/yumsure_db",
        description="SQLAlchemy-compatible database connection string for PostgreSQL via Psycopg 3."
    )

    # Alembic Migration Connection (Direct connection or Session Pooler port 5432)
    # Required for transactional DDL and schema migrations; falls back to DATABASE_URL if omitted.
    ALEMBIC_DATABASE_URL: Optional[str] = Field(
        default=None,
        description="Direct PostgreSQL connection string for Alembic migrations. Falls back to DATABASE_URL if not provided."
    )

    # Dedicated Isolated Test Database (Must NOT point to shared Supabase dev DB)
    TEST_DATABASE_URL: Optional[str] = Field(
        default=None,
        description="Dedicated isolated test database connection string. Required to run database integration tests."
    )

    # Connection Pool tuning for FastAPI application
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800  # Recycle connections after 30 minutes to prevent stale sockets

    # NVIDIA NIM AI Configuration
    NVIDIA_API_KEY: Optional[str] = Field(
        default=None,
        description="NVIDIA NIM API key for LLM explanations and topic-controlled chatbot."
    )
    NVIDIA_MODEL_NAME: str = Field(
        default="nvidia/llama-3.1-nemoguard-8b-topic-control",
        description="NVIDIA NIM model identifier."
    )
    NVIDIA_BASE_URL: str = Field(
        default="https://integrate.api.nvidia.com/v1",
        description="NVIDIA NIM base URL endpoint."
    )
    NVIDIA_MAX_TOKENS: int = 512
    NVIDIA_TEMPERATURE: float = 0.2

    @field_validator("DATABASE_URL", "ALEMBIC_DATABASE_URL", "TEST_DATABASE_URL", mode="before")
    @classmethod
    def validate_and_normalize_url(cls, v: Optional[str]) -> Optional[str]:
        return normalize_pg_url(v)

    model_config = SettingsConfigDict(
        env_file=(str(BACKEND_DIR / ".env"), ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )

    def get_masked_database_url(self) -> str:
        """Returns sanitized DATABASE_URL with password masked."""
        return mask_connection_url(self.DATABASE_URL)

    def get_masked_alembic_url(self) -> str:
        """Returns sanitized ALEMBIC_DATABASE_URL with password masked."""
        return mask_connection_url(self.get_alembic_database_url())

    def get_masked_test_url(self) -> str:
        """Returns sanitized TEST_DATABASE_URL with password masked."""
        return mask_connection_url(self.TEST_DATABASE_URL)

    def get_alembic_database_url(self) -> str:
        """
        Returns the effective URL for Alembic migrations.
        Uses ALEMBIC_DATABASE_URL if defined; falls back to DATABASE_URL.
        """
        return self.ALEMBIC_DATABASE_URL or self.DATABASE_URL


# Instantiate application settings singleton
settings = Settings()
