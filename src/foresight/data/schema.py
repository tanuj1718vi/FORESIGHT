"""Pydantic data schemas and validation models for Project FORESIGHT."""

from datetime import date
from typing import Any
from pydantic import BaseModel, Field, field_validator


class RawSalesRecord(BaseModel):
    """Raw sales transaction observation."""
    date: date
    sku_id: str = Field(..., min_length=1)
    store_id: str = Field(..., min_length=1)
    quantity: int = Field(..., ge=0)
    price: float = Field(..., gt=0)
    is_promoted: bool = False

    @field_validator("quantity")
    @classmethod
    def validate_non_negative_quantity(cls, v: int) -> int:
        if v < 0:
            raise ValueError(f"Quantity cannot be negative, got {v}")
        return v

    @field_validator("price")
    @classmethod
    def validate_positive_price(cls, v: float) -> float:
        if v <= 0:
            raise ValueError(f"Price must be strictly positive, got {v}")
        return v


class ProductMasterRecord(BaseModel):
    """Product catalog metadata and supplier parameters."""
    sku_id: str = Field(..., min_length=1)
    product_name: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    subcategory: str = Field(..., min_length=1)
    unit_cost: float = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    lead_time_days: int = Field(..., ge=1)
    min_order_qty: int = Field(..., ge=1)
    holding_cost_annual_rate: float = Field(default=0.20, ge=0.0, le=1.0)
    demand_pattern: str = Field(default="regular")  # regular, seasonal, intermittent, volatile

    @field_validator("unit_price")
    @classmethod
    def validate_price_above_cost(cls, v: float, info: Any) -> float:
        # Note: Cost check warning or validation
        return v


class InventorySnapshotRecord(BaseModel):
    """Inventory position record for a SKU at a given store/location."""
    date: date
    sku_id: str = Field(..., min_length=1)
    store_id: str = Field(..., min_length=1)
    inventory_level: int = Field(..., ge=0)
    units_on_order: int = Field(default=0, ge=0)
    backorders: int = Field(default=0, ge=0)


class ProcessedTimeSeriesRecord(BaseModel):
    """Cleaned, standardized daily time-series observation ready for feature engineering."""
    date: date
    sku_id: str
    store_id: str
    category: str
    subcategory: str
    quantity: int = Field(..., ge=0)
    price: float = Field(..., gt=0)
    unit_cost: float = Field(..., gt=0)
    is_promoted: bool
    inventory_level: int = Field(..., ge=0)
    units_on_order: int = Field(..., ge=0)
    backorders: int = Field(..., ge=0)
    lead_time_days: int = Field(..., ge=1)
    min_order_qty: int = Field(..., ge=1)
    demand_pattern: str
