"""Risk Assessment Record ORM model."""

from datetime import date, datetime
from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from foresight.database.base import Base


class RiskAssessmentRecord(Base):
    """Financial risk quantification, loss integrals, and risk classifications."""
    __tablename__ = "risk_assessment_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sku_id: Mapped[str] = mapped_column(String(50), ForeignKey("products.sku_id"), nullable=False, index=True)
    store_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    composite_risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    stockout_probability: Mapped[float] = mapped_column(Float, nullable=False)
    lost_revenue_risk: Mapped[float] = mapped_column(Float, nullable=False)
    lost_margin_risk: Mapped[float] = mapped_column(Float, nullable=False)
    excess_holding_cost_risk: Mapped[float] = mapped_column(Float, nullable=False)
    total_financial_exposure: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    product = relationship("Product", back_populates="risk_assessments")

    def __repr__(self) -> str:
        return f"<RiskAssessmentRecord(sku='{self.sku_id}', store='{self.store_id}', exposure=${self.total_financial_exposure:,.2f})>"
