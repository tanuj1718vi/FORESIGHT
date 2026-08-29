"""Prescriptive recommendation engine re-export for backward compatibility."""

from foresight.recommendations.engine import PrescriptiveEngine
from foresight.recommendations.schemas import PrescriptiveRecommendation

__all__ = ["PrescriptiveEngine", "PrescriptiveRecommendation"]
