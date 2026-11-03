import os
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import pool, create_engine as sa_create_engine
from sqlalchemy.pool import NullPool
from alembic import context

# -----------------------------------------------------------------------------
# Path Resolution: Add backend directory to sys.path
# -----------------------------------------------------------------------------
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Import settings and Base.metadata from application modules
from app.core.config import settings
from app.models import Base
from app.db.session import engine

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Generates raw SQL statements without establishing an active database connection.
    Uses ALEMBIC_DATABASE_URL if defined, falling back to DATABASE_URL.
    """
    url = settings.get_alembic_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        version_num_length=128,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    Establishes connection to PostgreSQL using ALEMBIC_DATABASE_URL if configured,
    or falls back to the application engine.
    Uses NullPool for dedicated migration connections to prevent pooled connection leaks.
    """
    if settings.ALEMBIC_DATABASE_URL:
        # Dedicated migration connection (e.g. direct Supabase connection on port 5432)
        connectable = sa_create_engine(
            settings.ALEMBIC_DATABASE_URL,
            poolclass=NullPool
        )
    else:
        # Reuses shared application engine
        connectable = engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            version_num_length=128,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
