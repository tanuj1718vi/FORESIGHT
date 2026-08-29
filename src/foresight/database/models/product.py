"""Product ORM model."""

from datetime import datetime
from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from foresight.database.base import Base, TimestampMixin


class Product(Base, TimestampMixin):
    """Product master entity representing SKU catalog attributes."""
    __tablename__ = "products"

    sku_id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    subcategory: Mapped[str] = mapped_column(String(100), nullable=False)
    unit_cost: Mapped[float] = mapped_column(Float, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    lead_time_days: Mapped[int] = mapped_column(Integer, nullable=False)
    min_order_qty: Mapped[int] = mapped_column(Integer, default=1)
    demand_pattern: Mapped[str] = mapped_column(String(50), default="regular")

    # Relationships
    sales = relationship("SalesRecord", back_populates="product", cascade="all, delete-orphan")
    inventory = relationship("InventoryRecord", back_populates="product", cascade="all, delete-orphan")
    forecasts = relationship("ForecastRecord", back_populates="product", cascade="all, delete-orphan")
    risk_assessments = relationship("RiskAssessmentRecord", back_populates="product", cascade="all, delete-orphan")
    recommendations = relationship("RecommendationRecord", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Product(sku_id='{self.sku_id}', name='{self.product_name}', cat='{self.category}')>"
