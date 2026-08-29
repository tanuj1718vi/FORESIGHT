"""Model Run ORM model."""

from datetime import datetime
from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from foresight.database.base import Base


class ModelRun(Base):
    """Model training, evaluation, and experiment registry records."""
    __tablename__ = "model_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    model_version: Mapped[str] = mapped_column(String(50), default="1.0.0")
    training_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    dataset_version: Mapped[str] = mapped_column(String(100), default="v1.0")
    metrics_json: Mapped[str] = mapped_column(Text, nullable=False, comment="JSON serialized metrics (WAPE, RMSE, etc.)")
    parameters_json: Mapped[str] = mapped_column(Text, nullable=False, comment="JSON serialized hyperparameters")
    artifact_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_champion: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<ModelRun(run_id='{self.run_id}', name='{self.model_name}', champ={self.is_champion})>"
