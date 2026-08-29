"""Recommendation repository."""

from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session

from foresight.database.models.recommendation import RecommendationRecord
from foresight.database.repositories.base_repository import BaseRepository


class RecommendationRepository(BaseRepository[RecommendationRecord]):
    """Repository handling Prescriptive action work orders and rebalance tasks."""

    def __init__(self, session: Session) -> None:
        super().__init__(RecommendationRecord, session)

    def get_by_recommendation_id(self, rec_id: str) -> RecommendationRecord | None:
        """Fetch recommendation by unique identifier."""
        stmt = select(RecommendationRecord).where(RecommendationRecord.recommendation_id == rec_id)
        return self.session.scalars(stmt).first()

    def list_by_action(self, action: str) -> Sequence[RecommendationRecord]:
        """Fetch work orders matching a specific action (ORDER, EXPEDITE, REBALANCE, etc.)."""
        stmt = select(RecommendationRecord).where(RecommendationRecord.action == action)
        return self.session.scalars(stmt).all()

    def list_by_urgency(self, urgency: str) -> Sequence[RecommendationRecord]:
        """Fetch work orders matching an urgency level."""
        stmt = select(RecommendationRecord).where(RecommendationRecord.urgency == urgency)
        return self.session.scalars(stmt).all()
