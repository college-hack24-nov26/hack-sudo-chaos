"""
YumSure Repositories Package.

Data Access Layer (DAL) providing domain-oriented query and persistence interfaces.
"""

from app.repositories.product_repository import ProductRepository

__all__ = ["ProductRepository"]

