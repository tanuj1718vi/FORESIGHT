"""Inventory repository."""

from datetime import date
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session

from foresight.database.models.inventory import InventoryRecord
from foresight.database.repositories.base_repository import BaseRepository


class InventoryRepository(BaseRepository[InventoryRecord]):
    """Repository handling daily Inventory snapshot records."""

    def __init__(self, session: Session) -> None:
        super().__init__(InventoryRecord, session)

    def get_latest_position(self, sku_id: str, store_id: str) -> InventoryRecord | None:
        """Fetch the latest inventory state for a specific SKU-Store node."""
        stmt = (
            select(InventoryRecord)
            .where(InventoryRecord.sku_id == sku_id, InventoryRecord.store_id == store_id)
            .order_by(InventoryRecord.date.desc())
            .limit(1)
        )
        return self.session.scalars(stmt).first()

    def list_by_sku(self, sku_id: str, limit: int = 100) -> Sequence[InventoryRecord]:
        """Fetch inventory history across stores for a SKU."""
        stmt = select(InventoryRecord).where(InventoryRecord.sku_id == sku_id).order_by(InventoryRecord.date.desc()).limit(limit)
        return self.session.scalars(stmt).all()
