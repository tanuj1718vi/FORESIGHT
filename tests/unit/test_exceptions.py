"""Unit tests for domain exceptions hierarchy."""

import pytest

from foresight.utils.exceptions import (
    ConfigurationError,
    DataLeakageError,
    DataProcessingError,
    DataValidationError,
    FeatureEngineeringError,
    ForecastError,
    ForesightError,
    InventoryOptimizationError,
    ModelTrainingError,
    RecommendationError,
    RiskEngineError,
)


@pytest.mark.unit
def test_foresight_base_exception() -> None:
    """Verify ForesightError stores message and details payload."""
    details = {"field": "lead_time", "value": -5}
    err = ForesightError("Invalid lead time", details=details)

    assert str(err) == "Invalid lead time"
    assert err.message == "Invalid lead time"
    assert err.details == details


@pytest.mark.unit
def test_exception_inheritance() -> None:
    """Verify domain exceptions properly subclass ForesightError and specialized classes."""
    assert issubclass(ConfigurationError, ForesightError)
    assert issubclass(DataValidationError, ForesightError)
    assert issubclass(DataProcessingError, ForesightError)
    assert issubclass(FeatureEngineeringError, ForesightError)
    assert issubclass(DataLeakageError, FeatureEngineeringError)
    assert issubclass(DataLeakageError, ForesightError)
    assert issubclass(ModelTrainingError, ForesightError)
    assert issubclass(ForecastError, ForesightError)
    assert issubclass(InventoryOptimizationError, ForesightError)
    assert issubclass(RiskEngineError, ForesightError)
    assert issubclass(RecommendationError, ForesightError)


@pytest.mark.unit
def test_raising_and_catching_specialized_exception() -> None:
    """Verify catching base exception intercepts derived domain exceptions."""
    with pytest.raises(ForesightError) as exc_info:
        raise DataLeakageError("Future lag feature detected in training window")

    assert isinstance(exc_info.value, DataLeakageError)
    assert isinstance(exc_info.value, FeatureEngineeringError)
    assert "Future lag feature" in str(exc_info.value)
