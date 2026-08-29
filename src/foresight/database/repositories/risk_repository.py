"""Risk repository."""

from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session

from foresight.database.models.risk_assessment import RiskAssessmentRecord
from foresight.database.repositories.base_repository import BaseRepository


class RiskRepository(BaseRepository[RiskAssessmentRecord]):
    """Repository handling Risk assessment and financial exposure records."""

    def __init__(self, session: Session) -> None:
        super().__init__(RiskAssessmentRecord, session)

    def get_latest_assessment(self, sku_id: str, store_id: str) -> RiskAssessmentRecord | None:
        """Fetch the most recent risk score for a SKU-Store node."""
        stmt = (
            select(RiskAssessmentRecord)
            .where(RiskAssessmentRecord.sku_id == sku_id, RiskAssessmentRecord.store_id == store_id)
            .order_by(RiskAssessmentRecord.date.desc())
            .limit(1)
        )
        return self.session.scalars(stmt).first()

    def list_critical_risks(self, limit: int = 20) -> Sequence[RiskAssessmentRecord]:
        """Fetch nodes sorted by highest financial exposure."""
        stmt = (
            select(RiskAssessmentRecord)
            .order_by(RiskAssessmentRecord.total_financial_exposure.desc())
            .limit(limit)
        )
        return self.session.scalars(stmt).all()
