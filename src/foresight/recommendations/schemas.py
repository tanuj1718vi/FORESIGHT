"""Prescriptive recommendation schemas and action definitions."""

from pydantic import BaseModel, Field
from foresight.config.constants import RecommendationAction, RecommendationUrgency

class Recommendation(BaseModel):
    """Prescriptive operational recommendation."""
    recommendation_id: str
    sku_id: str
    store_id: str
    action: RecommendationAction
    recommended_quantity: float = Field(default=0.0, ge=0.0)
    urgency: RecommendationUrgency
    justification: str
    expected_financial_impact: float = Field(default=0.0, ge=0.0)
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    donor_store_id: str | None = None

# Backward compatibility alias
PrescriptiveRecommendation = Recommendation
