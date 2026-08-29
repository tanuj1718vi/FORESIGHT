"""Forecast API request and response Pydantic schemas."""

from pydantic import BaseModel, Field


class ForecastRequest(BaseModel):
    """Single observation demand forecasting request."""
    sku_id: str = Field(..., json_schema_extra={"example": "SKU-1001"})
    store_id: str = Field(..., json_schema_extra={"example": "STORE-001"})
    date: str = Field(..., json_schema_extra={"example": "2024-08-01"})
    features: dict[str, float | int] = Field(..., description="Engineered feature key-value pairs")


class ForecastResponse(BaseModel):
    """Point forecast response with prediction intervals."""
    sku_id: str
    store_id: str
    date: str
    predicted_demand: float = Field(..., ge=0.0, description="Point forecast (units/day)")
    p10_lower_bound: float | None = Field(default=None, ge=0.0, description="10th percentile conservative bound")
    p90_upper_bound: float | None = Field(default=None, ge=0.0, description="90th percentile optimistic bound")
    model_name: str = "XGBoost"


class BatchForecastRequest(BaseModel):
    """Batch demand forecasting request payload."""
    items: list[ForecastRequest]


class BatchForecastResponse(BaseModel):
    """Batch demand forecasting response payload."""
    total_items: int
    predictions: list[ForecastResponse]
