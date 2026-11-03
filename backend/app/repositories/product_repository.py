"""
Product Repository Implementation.

Provides clean, read-focused Data Access Layer (DAL) operations for Product entities,
eliminating N+1 queries using targeted SQLAlchemy 2.0 eager-loading strategies.
"""

import uuid
from typing import Optional, Union
from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.product import Product
from app.models.product_nutrient import ProductNutrient
from app.models.product_ingredient import ProductIngredient


class ProductRepository:
    """
    Repository handling data access and retrieval for Products and their
    associated 3NF relationships (nutrients, ingredients, data sources).
    """

    def __init__(self, session: Session) -> None:
        """
        Initializes repository with an active SQLAlchemy session.
        Session lifecycle (commit/rollback/close) is managed by the caller.
        """
        self.session = session

    def get_by_barcode(
        self,
        barcode: str,
        load_relationships: bool = True
    ) -> Optional[Product]:
        """
        Retrieves a single Product by its unique barcode (EAN-13, UPC-A, etc.).

        When load_relationships is True (default):
        - Eagerly loads `data_source` via joinedload (single-row join).
        - Eagerly loads `nutrients` + master `Nutrient` via selectinload.
        - Eagerly loads `ingredients` + master `Ingredient` via selectinload.
          Ingredients are ordered by integer sequence_order ascending (1, 2, 3...),
          representing the descending order of ingredient weight as declared on the product label.
        
        Avoids N+1 query overhead and prevents Cartesian row explosion.
        Returns None if no matching product exists.
        """
        clean_barcode = barcode.strip() if barcode else ""
        if not clean_barcode:
            return None

        stmt = select(Product).where(Product.barcode == clean_barcode)

        if load_relationships:
            stmt = stmt.options(
                joinedload(Product.data_source),
                selectinload(Product.nutrients).joinedload(ProductNutrient.nutrient),
                selectinload(Product.ingredients).joinedload(ProductIngredient.ingredient),
            )

        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def get_by_id(
        self,
        product_id: Union[uuid.UUID, str],
        load_relationships: bool = True
    ) -> Optional[Product]:
        """
        Retrieves a Product by its primary key UUID.
        Returns None if not found.
        """
        if isinstance(product_id, str):
            try:
                product_id = uuid.UUID(product_id)
            except ValueError:
                return None

        stmt = select(Product).where(Product.id == product_id)

        if load_relationships:
            stmt = stmt.options(
                joinedload(Product.data_source),
                selectinload(Product.nutrients).joinedload(ProductNutrient.nutrient),
                selectinload(Product.ingredients).joinedload(ProductIngredient.ingredient),
            )

        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def exists_by_barcode(self, barcode: str) -> bool:
        """
        High-performance existence check.
        Issues a lightweight COUNT(1) query without allocating ORM instances.
        """
        clean_barcode = barcode.strip() if barcode else ""
        if not clean_barcode:
            return False

        stmt = (
            select(func.count())
            .select_from(Product)
            .where(Product.barcode == clean_barcode)
        )
        count = self.session.execute(stmt).scalar_one()
        return count > 0

    def get_verified_by_barcode(self, barcode: str) -> Optional[Product]:
        """
        Retrieves a product only if it has been marked as verified (is_verified = True).
        Used by caching and external update guards to protect curated data.
        """
        clean_barcode = barcode.strip() if barcode else ""
        if not clean_barcode:
            return None

        stmt = (
            select(Product)
            .where(Product.barcode == clean_barcode, Product.is_verified.is_(True))
            .options(
                joinedload(Product.data_source),
                selectinload(Product.nutrients).joinedload(ProductNutrient.nutrient),
                selectinload(Product.ingredients).joinedload(ProductIngredient.ingredient),
            )
        )
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

