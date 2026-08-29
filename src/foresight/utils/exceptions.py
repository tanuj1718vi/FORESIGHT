"""Domain exceptions hierarchy for Project FORESIGHT."""


class ForesightError(Exception):
    """Base exception for all errors in Project FORESIGHT."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConfigurationError(ForesightError):
    """Raised when application or environment configuration is invalid."""


class DataValidationError(ForesightError):
    """Raised when data fails quality, schema, or integrity constraints."""


class DataProcessingError(ForesightError):
    """Raised when data transformation, ingestion, or cleaning fails."""


class FeatureEngineeringError(ForesightError):
    """Raised when feature generation fails or data leakage is detected."""


class DataLeakageError(FeatureEngineeringError):
    """Raised when future information leaks into historical training features."""


class ModelTrainingError(ForesightError):
    """Raised when model training or hyperparameter optimization fails."""


class ForecastError(ForesightError):
    """Raised during forecast inference, horizon generation, or uncertainty estimation."""


# Alias for ForecastError
ForecastingError = ForecastError


class InventoryOptimizationError(ForesightError):
    """Raised when inventory calculation (Safety Stock, ROP, EOQ) receives invalid parameters."""


class RiskEngineError(ForesightError):
    """Raised when risk score computation or threshold evaluation fails."""


class RecommendationError(ForesightError):
    """Raised when prescriptive recommendation engine cannot resolve an action."""


class DatabaseError(ForesightError):
    """Raised when database operations fail."""
