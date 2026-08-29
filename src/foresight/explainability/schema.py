"""Pydantic schemas and data models for the Model Explainability Engine."""

from datetime import datetime
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class FeatureCategory(str, Enum):
    """Categorical grouping of engineered features."""
    TEMPORAL = "temporal"
    AUTOREGRESSIVE_LAG = "autoregressive_lag"
    ROLLING_STATS = "rolling_stats"
    VELOCITY_TREND = "velocity_trend"
    PRICING_PROMO = "pricing_promo"
    OPERATIONAL = "operational"
    CATEGORICAL_HIERARCHY = "categorical_hierarchy"


class GlobalFeatureImportance(BaseModel):
    """Global feature importance score derived from mean absolute SHAP values."""
    feature_name: str
    category: FeatureCategory
    mean_abs_shap: float = Field(..., ge=0.0, description="Mean absolute SHAP impact in prediction units")
    rank: int = Field(..., ge=1)
    relative_importance_pct: float = Field(..., ge=0.0, le=100.0)


class DriverContribution(BaseModel):
    """Individual feature contribution to a specific local prediction."""
    feature_name: str
    feature_value: float | int | str
    attribution_units: float = Field(..., description="SHAP attribution (positive pushes demand up, negative down)")
    percentage_contribution: float


class LocalExplanation(BaseModel):
    """Comprehensive local driver attribution for an individual SKU-Store-Date prediction."""
    sku_id: str
    store_id: str
    date: str
    base_value: float = Field(..., description="Expected model baseline output E[y]")
    predicted_value: float = Field(..., description="Model final point prediction y_hat")
    top_positive_drivers: list[DriverContribution]
    top_negative_drivers: list[DriverContribution]
    business_narrative: str = Field(..., description="Executive natural language justification")


class ExplainabilityReport(BaseModel):
    """Complete enterprise model explainability audit report."""
    audit_date: str = Field(default_factory=lambda: datetime.now().isoformat())
    model_name: str
    sample_records_evaluated: int
    global_feature_importances: list[GlobalFeatureImportance]
    category_importance_breakdown: dict[str, float]
    sample_explanations: list[LocalExplanation]

    def to_markdown(self) -> str:
        """Render explainability audit report as clean GitHub Flavored Markdown."""
        lines = [
            f"# FORESIGHT — Machine Learning Explainability & Driver Decomposition Report",
            f"",
            f"**Audit Timestamp:** `{self.audit_date}`  ",
            f"**Forecasting Model:** `{self.model_name}`  ",
            f"**Explainability Methodology:** TreeSHAP (Additive Shapley Values)  ",
            f"**Evaluation Sample Size:** `{self.sample_records_evaluated:,}` observations  ",
            f"",
            f"---",
            f"",
            f"## 1. Top 15 Global Demand Drivers (SHAP Value Ranking)",
            f"",
            f"| Rank | Feature Name | Feature Group | Mean |SHAP| (Units) | Relative Share |",
            f"| :---: | :--- | :---: | :---: | :---: |",
        ]

        for feat in self.global_feature_importances[:15]:
            lines.append(
                f"| {feat.rank} | `{feat.feature_name}` | `{feat.category.value}` | **{feat.mean_abs_shap:.3f}** | `{feat.relative_importance_pct:.1f}%` |"
            )

        lines.extend([
            f"",
            f"---",
            f"",
            f"## 2. Feature Group Importance Breakdown",
            f"",
            f"| Feature Category | Aggregate Relative Impact (%) |",
            f"| :--- | :---: |",
        ])

        for cat, pct in sorted(self.category_importance_breakdown.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"| `{cat}` | **{pct:.1f}%** |")

        lines.extend([
            f"",
            f"---",
            f"",
            f"## 3. Sample Local Forecast Explanations & Business Narratives",
            f"",
        ])

        for i, exp in enumerate(self.sample_explanations, start=1):
            lines.extend([
                f"### Explanation #{i}: SKU `{exp.sku_id}` at Store `{exp.store_id}` ({exp.date})",
                f"- **Baseline Demand \\(E[y]\\):** `{exp.base_value:.1f} units`",
                f"- **Predicted Demand \\(\\hat{{y}}\\):** **{exp.predicted_value:.1f} units**",
                f"- **Executive Narrative:** *{exp.business_narrative}*",
                f"",
                f"| Driver Feature | Actual Value | Impact on Demand |",
                f"| :--- | :---: | :---: |",
            ])
            for d in exp.top_positive_drivers:
                lines.append(f"| `{d.feature_name}` (Positive) | `{d.feature_value}` | **+{d.attribution_units:.2f} units** |")
            for d in exp.top_negative_drivers:
                lines.append(f"| `{d.feature_name}` (Negative) | `{d.feature_value}` | **{d.attribution_units:.2f} units** |")
            lines.append("")

        return "\n".join(lines)
