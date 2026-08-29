"""Inventory optimization API request and response schemas."""

from pydantic import BaseModel, Field

from foresight.inventory.schema import InventoryHealthStatus, SafetyStockMethod


class InventoryOptimizeRequest(BaseModel):
    """Single SKU inventory optimization request."""
    sku_id: str = Field(..., json_schema_extra={"example": "SKU-1001"})
    store_id: str = Field(..., json_schema_extra={"example": "STORE-001"})
    current_on_hand: float = Field(..., ge=0.0, json_schema_extra={"example": 50.0})
    units_on_order: float = Field(default=0.0, ge=0.0, json_schema_extra={"example": 0.0})
    backorders: float = Field(default=0.0, ge=0.0, json_schema_extra={"example": 0.0})
    unit_cost: float = Field(..., gt=0.0, json_schema_extra={"example": 25.0})
    unit_price: float = Field(..., gt=0.0, json_schema_extra={"example": 55.0})
    lead_time_days: float = Field(..., gt=0.0, json_schema_extra={"example": 7.0})
    lead_time_std_days: float = Field(default=1.0, ge=0.0, json_schema_extra={"example": 1.0})
    holding_cost_annual_rate: float = Field(default=0.20, gt=0.0, json_schema_extra={"example": 0.20})
    fixed_order_cost: float = Field(default=50.0, ge=0.0, json_schema_extra={"example": 50.0})
    min_order_qty: float = Field(default=1.0, ge=1.0, json_schema_extra={"example": 10.0})
    target_service_level: float = Field(default=0.95, ge=0.50, lt=1.0, json_schema_extra={"example": 0.95})
    forecast_daily_demand_mean: float = Field(..., gt=0.0, json_schema_extra={"example": 20.0})
    forecast_daily_demand_std: float = Field(..., gt=0.0, json_schema_extra={"example": 4.0})
    method: SafetyStockMethod = Field(default=SafetyStockMethod.COMBINED_UNCERTAINTY)


class InventoryOptimizeResponse(BaseModel):
    """Optimized inventory replenishment policy."""
    sku_id: str
    store_id: str
    net_stock: float
    safety_stock: float
    reorder_point: float
    economic_order_quantity: float
    recommended_order_quantity: float
    days_of_supply: float
    stockout_risk_prob: float
    health_status: InventoryHealthStatus
    recommended_action: str
    working_capital_committed: float
    total_annual_inventory_cost: float


class BatchInventoryOptimizeRequest(BaseModel):
    """Batch inventory optimization request."""
    items: list[InventoryOptimizeRequest]


class BatchInventoryOptimizeResponse(BaseModel):
    """Batch inventory optimization response."""
    total_items: int
    results: list[InventoryOptimizeResponse]
