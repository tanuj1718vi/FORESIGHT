"""Unit tests for NarrativeGenerator."""

import pytest

from foresight.explainability.narrative import NarrativeGenerator
from foresight.explainability.schema import DriverContribution


@pytest.mark.explainability
def test_generate_narrative_promotional_surge() -> None:
    """Verify narrative synthesis for a promotion-driven demand surge."""
    pos_drivers = [
        DriverContribution(feature_name="is_promoted", feature_value=1, attribution_units=8.5, percentage_contribution=60.0),
        DriverContribution(feature_name="is_weekend", feature_value=1, attribution_units=3.2, percentage_contribution=22.0),
    ]
    neg_drivers = [
        DriverContribution(feature_name="price", feature_value=45.0, attribution_units=-1.2, percentage_contribution=8.0)
    ]

    narrative = NarrativeGenerator.generate_narrative(
        sku_id="SKU-1001",
        base_value=20.0,
        predicted_value=30.5,
        positive_drivers=pos_drivers,
        negative_drivers=neg_drivers,
    )

    assert "SKU-1001" in narrative
    assert "30.5 units" in narrative
    assert "promotional" in narrative.lower()
    assert "weekend" in narrative.lower()


@pytest.mark.explainability
def test_generate_narrative_neutral_baseline() -> None:
    """Verify narrative synthesis when forecast matches baseline."""
    narrative = NarrativeGenerator.generate_narrative(
        sku_id="SKU-1002",
        base_value=25.0,
        predicted_value=25.1,
        positive_drivers=[],
        negative_drivers=[],
    )

    assert "SKU-1002" in narrative
    assert "closely matching" in narrative.lower()
