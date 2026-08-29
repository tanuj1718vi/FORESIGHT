"""Explainability API request and response schemas."""

from pydantic import BaseModel, Field

from foresight.explainability.schema import DriverContribution


class ExplainRequest(BaseModel):
    """Local SHAP driver explanation request."""
    sku_id: str = Field(..., json_schema_extra={"example": "SKU-1001"})
    store_id: str = Field(..., json_schema_extra={"example": "STORE-001"})
    date: str = Field(..., json_schema_extra={"example": "2024-08-01"})
    features: dict[str, float | int] = Field(..., description="Engineered feature values")


class ExplainResponse(BaseModel):
    """Local SHAP driver explanation response with executive narrative."""
    sku_id: str
    store_id: str
    date: str
    base_value: float
    predicted_value: float
    top_positive_drivers: list[DriverContribution]
    top_negative_drivers: list[DriverContribution]
    business_narrative: str
