"""Prescriptive recommendation and decision intelligence package for Project FORESIGHT."""

from foresight.recommendations.engine import PrescriptiveEngine
from foresight.recommendations.explanations import build_recommendation_justification
from foresight.recommendations.rules import evaluate_action_rule
from foresight.recommendations.schemas import PrescriptiveRecommendation, Recommendation
from foresight.recommendations.scoring import calculate_recommendation_confidence

__all__ = [
    "PrescriptiveEngine",
    "Recommendation",
    "PrescriptiveRecommendation",
    "evaluate_action_rule",
    "calculate_recommendation_confidence",
    "build_recommendation_justification",
]
