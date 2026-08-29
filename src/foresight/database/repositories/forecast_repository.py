"""Forecast repository."""

from datetime import date
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session

from foresight.database.models.forecast import ForecastRecord
from foresight.database.repositories.base_repository import BaseRepository


class ForecastRepository(BaseRepository[ForecastRecord]):
    """Repository handling Forecast trajectory records."""

    def __init__(self, session: Session) -> None:
        super().__init__(ForecastRecord, session)

    def list_future_forecasts(
        self,
        sku_id: str,
        store_id: str,
        from_date: date | None = None,
        limit: int = 60,
    ) -> Sequence[ForecastRecord]:
        """Fetch forward forecast sequence for a SKU-Store node."""
        stmt = select(ForecastRecord).where(
            ForecastRecord.sku_id == sku_id,
            ForecastRecord.store_id == store_id,
        )
        if from_date:
            stmt = stmt.where(ForecastRecord.prediction_date >= from_date)
        stmt = stmt.order_by(ForecastRecord.prediction_date.asc()).limit(limit)
        return self.session.scalars(stmt).all()
