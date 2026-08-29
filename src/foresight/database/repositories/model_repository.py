"""Model repository."""

from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session

from foresight.database.models.model_run import ModelRun
from foresight.database.repositories.base_repository import BaseRepository


class ModelRepository(BaseRepository[ModelRun]):
    """Repository handling Model run tracking and champion registry."""

    def __init__(self, session: Session) -> None:
        super().__init__(ModelRun, session)

    def get_champion(self) -> ModelRun | None:
        """Fetch the active champion model run."""
        stmt = select(ModelRun).where(ModelRun.is_champion.is_(True)).order_by(ModelRun.created_at.desc()).limit(1)
        return self.session.scalars(stmt).first()

    def get_by_run_id(self, run_id: str) -> ModelRun | None:
        """Fetch model run by run ID."""
        stmt = select(ModelRun).where(ModelRun.run_id == run_id)
        return self.session.scalars(stmt).first()

    def list_recent_runs(self, limit: int = 10) -> Sequence[ModelRun]:
        """Fetch recent experiment runs."""
        stmt = select(ModelRun).order_by(ModelRun.created_at.desc()).limit(limit)
        return self.session.scalars(stmt).all()
