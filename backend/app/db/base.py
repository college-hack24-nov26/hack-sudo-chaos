"""
SQLAlchemy 2.0 Declarative Base Definition.

All ORM entity models in YumSure inherit from this Base class to register
their schema metadata with SQLAlchemy and Alembic.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Top-level DeclarativeBase for SQLAlchemy 2.0.
    Provides metadata tracking and a standardized string representation.
    """
    def __repr__(self) -> str:
        # Standardized representation showing class name and primary key attributes
        cols = []
        for col in self.__table__.columns:
            if col.primary_key:
                val = getattr(self, col.name, None)
                cols.append(f"{col.name}={val!r}")
        return f"<{self.__class__.__name__}({', '.join(cols)})>"

