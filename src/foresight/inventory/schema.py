"""Pydantic data contracts and schemas for the Inventory Optimization Engine."""

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class SafetyStockMethod(str, Enum):
    """Supported mathematical methods for safety stock estimation."""
    COMBINED_UNCERTAINTY = "combined_uncertainty"
    DEMAND_ONLY = "demand_only"
    LEAD_TIME_ONLY = "lead_time_only"
    QUANTILE_ML = "quantile_ml"


class InventoryHealthStatus(str, Enum):
    """Categorical assessment of current stock position."""
    OPTIMAL = "OPTIMAL"
    UNDERSTOCKED = "UNDERSTOCKED"
    STOCKOUT_IMMINENT = "STOCKOUT_IMMINENT"
    OVERSTOCKED = "OVERSTOCKED"
    CRITICAL_EXCESS = "CRITICAL_EXCESS"


class OrderAction(str, Enum):
    """Prescriptive inventory operational recommendation."""
    ORDER = "ORDER"
    HOLD = "HOLD"
    EXPEDITE = "EXPEDITE"
    REDUCE = "REDUCE"


class InventoryParameters(BaseModel):
    """Input operational parameters for inventory policy optimization."""
    sku_id: str
    store_id: str
    current_on_hand: float = Field(..., ge=0, description="Current physical units on shelf/warehouse")
    units_on_order: float = Field(default=0.0, ge=0, description="In-transit purchase orders")
    backorders: float = Field(default=0.0, ge=0, description="Unfulfilled committed customer demand")
    unit_cost: float = Field(..., gt=0, description="Cost of Goods Sold per unit")
    unit_price: float = Field(..., gt=0, description="Catalog retail selling price")
    lead_time_days: float = Field(..., gt=0, description="Supplier replenishment lead time in days")
    lead_time_std_days: float = Field(default=1.0, ge=0, description="Lead time variance standard deviation")
    holding_cost_annual_rate: float = Field(default=0.20, gt=0, description="Annual capital & holding cost rate (e.g. 0.20 for 20%)")
    fixed_order_cost: float = Field(default=50.0, gt=0, description="Fixed administrative setup cost per PO")
    min_order_qty: float = Field(default=1.0, ge=1.0, description="Supplier Minimum Order Quantity (MOQ)")
    target_service_level: float = Field(default=0.95, gt=0.5, lt=1.0, description="Target cycle service level (e.g. 0.95)")
    forecast_daily_demand_mean: float = Field(..., ge=0, description="Expected daily sales rate")
    forecast_daily_demand_std: float = Field(..., ge=0, description="Daily sales standard deviation")
    forecast_daily_demand_p95: float | None = Field(default=None, description="95th percentile daily forecast")


class InventoryOptimizationResult(BaseModel):
    """Output optimization parameters, safety buffers, and order recommendations."""
    sku_id: str
    store_id: str
    service_level: float
    z_score: float
    safety_stock: float
    lead_time_demand: float
    reorder_point: float
    net_stock: float
    days_of_supply: float
    economic_order_quantity: float
    recommended_order_quantity: float
    reorder_triggered: bool
    recommended_action: OrderAction
    health_status: InventoryHealthStatus
    stockout_risk_prob: float
    working_capital_committed: float
    annual_holding_cost: float
    annual_ordering_cost: float
    total_annual_inventory_cost: float
