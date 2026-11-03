"""
SQLAlchemy 2.0 Engine, Connection Pool, and Session Lifecycle Management.

Configures synchronous connection pooling with Psycopg 3 for PostgreSQL 18,
defines the thread-safe sessionmaker, and provides the FastAPI get_db dependency.
"""

from typing import Generator, Tuple
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize the SQLAlchemy 2.0 Synchronous Engine with Psycopg 3
# pool_pre_ping=True: executes 'SELECT 1' before handing a connection to prevent stale socket errors
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=True,
    echo=False  # Set to True in debugging if query logging is needed
)

# Session factory bound to the engine
# autocommit=False ensures transactions are explicitly committed
# autoflush=False prevents unexpected flushes before query execution
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=Session
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a SQLAlchemy database session per request
    and guarantees its closure upon request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connectivity() -> Tuple[bool, str]:
    """
    Verifies actual database connectivity by executing a lightweight ping query (SELECT 1;).
    Returns (True, 'Connected') on success or (False, error_message) on failure.
    Safely catches exceptions without leaking passwords.
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1;")).scalar()
            if result == 1:
                return True, "Database connection verified successfully (SELECT 1)."
            return False, f"Unexpected ping result: {result}"
    except SQLAlchemyError as err:
        # Strip credentials if any are embedded in the error string
        err_str = str(err)
        masked_url = settings.get_masked_database_url()
        return False, f"Database connectivity failed against {masked_url}. Details: {err_str}"
    except Exception as exc:
        return False, f"Unexpected error during connectivity check: {str(exc)}"

