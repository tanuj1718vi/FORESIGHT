"""Sales repository."""

from datetime import date
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session

from foresight.database.models.sales import SalesRecord
from foresight.database.repositories.base_repository import BaseRepository


class SalesRepository(BaseRepository[SalesRecord]):
    """Repository handling Sales transactional records."""

    def __init__(self, session: Session) -> None:
        super().__init__(SalesRecord, session)

    def list_by_sku_and_store(
        self,
        sku_id: str,
        store_id: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int = 1000,
    ) -> Sequence[SalesRecord]:
        """Fetch sales time-series for a specific SKU and optional store."""
        stmt = select(SalesRecord).where(SalesRecord.sku_id == sku_id)
        if store_id:
            stmt = stmt.where(SalesRecord.store_id == store_id)
        if start_date:
            stmt = stmt.where(SalesRecord.date >= start_date)
        if end_date:
            stmt = stmt.where(SalesRecord.date <= end_date)
        stmt = stmt.order_by(SalesRecord.date.asc()).limit(limit)
        return self.session.scalars(stmt).all()
