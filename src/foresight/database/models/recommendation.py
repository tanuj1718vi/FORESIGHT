"""Recommendation Record ORM model."""

from datetime import date, datetime
from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from foresight.database.base import Base


class RecommendationRecord(Base):
    """Prescriptive action work orders and lateral rebalance transfers."""
    __tablename__ = "recommendation_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    recommendation_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    sku_id: Mapped[str] = mapped_column(String(50), ForeignKey("products.sku_id"), nullable=False, index=True)
    store_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    donor_store_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    recommended_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    urgency: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    expected_financial_impact: Mapped[float] = mapped_column(Float, default=0.0)
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    justification: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    product = relationship("Product", back_populates="recommendations")

    def __repr__(self) -> str:
        return f"<RecommendationRecord(id='{self.recommendation_id}', action='{self.action}', sku='{self.sku_id}', qty={self.recommended_quantity})>"
