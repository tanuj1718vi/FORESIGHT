"""Inventory Record ORM model."""

from datetime import date, datetime
from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from foresight.database.base import Base


class InventoryRecord(Base):
    """Daily on-hand and supply chain inventory state observations."""
    __tablename__ = "inventory_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sku_id: Mapped[str] = mapped_column(String(50), ForeignKey("products.sku_id"), nullable=False, index=True)
    store_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    inventory_level: Mapped[int] = mapped_column(Integer, nullable=False)
    units_on_order: Mapped[int] = mapped_column(Integer, default=0)
    backorders: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    product = relationship("Product", back_populates="inventory")

    def __repr__(self) -> str:
        return f"<InventoryRecord(sku='{self.sku_id}', store='{self.store_id}', date='{self.date}', on_hand={self.inventory_level})>"
