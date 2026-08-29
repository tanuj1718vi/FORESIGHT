"""Model explainability, SHAP feature attributions, and driver decomposition."""

from foresight.explainability.narrative import NarrativeGenerator
from foresight.explainability.run_explainability import (
    ExplainabilityReport,
    run_explainability_audit,
)
from foresight.explainability.schema import (
    DriverContribution,
    FeatureCategory,
    GlobalFeatureImportance,
    LocalExplanation,
)
from foresight.explainability.shap_explainer import ForecastExplainer

__all__ = [
    "FeatureCategory",
    "GlobalFeatureImportance",
    "DriverContribution",
    "LocalExplanation",
    "ExplainabilityReport",
    "ForecastExplainer",
    "NarrativeGenerator",
    "run_explainability_audit",
]
