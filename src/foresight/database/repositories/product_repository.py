"""Product repository."""

from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session

from foresight.database.models.product import Product
from foresight.database.repositories.base_repository import BaseRepository


class ProductRepository(BaseRepository[Product]):
    """Repository handling Product master queries."""

    def __init__(self, session: Session) -> None:
        super().__init__(Product, session)

    def get_by_sku(self, sku_id: str) -> Product | None:
        """Fetch product by SKU code."""
        return self.session.get(Product, sku_id)

    def list_by_category(self, category: str) -> Sequence[Product]:
        """Fetch all products in a given category."""
        stmt = select(Product).where(Product.category == category)
        return self.session.scalars(stmt).all()

    def get_all_categories(self) -> Sequence[str]:
        """Get distinct product categories."""
        stmt = select(Product.category).distinct()
        return self.session.scalars(stmt).all()
