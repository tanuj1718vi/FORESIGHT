"""API schema package exports."""

from foresight.api.schemas.common import (
    ErrorResponse,
    HealthResponse,
    ReadinessResponse,
    VersionResponse,
)
from foresight.api.schemas.explain import ExplainRequest, ExplainResponse
from foresight.api.schemas.forecast import (
    BatchForecastRequest,
    BatchForecastResponse,
    ForecastRequest,
    ForecastResponse,
)
from foresight.api.schemas.inventory import (
    BatchInventoryOptimizeRequest,
    BatchInventoryOptimizeResponse,
    InventoryOptimizeRequest,
    InventoryOptimizeResponse,
)
from foresight.api.schemas.risk import (
    PrescriptiveRequest,
    PrescriptiveResponse,
    RiskAssessRequest,
    RiskAssessResponse,
    ScenarioSimulateRequest,
    ScenarioSimulateResponse,
)

__all__ = [
    "HealthResponse",
    "ReadinessResponse",
    "VersionResponse",
    "ErrorResponse",
    "ForecastRequest",
    "ForecastResponse",
    "BatchForecastRequest",
    "BatchForecastResponse",
    "InventoryOptimizeRequest",
    "InventoryOptimizeResponse",
    "BatchInventoryOptimizeRequest",
    "BatchInventoryOptimizeResponse",
    "RiskAssessRequest",
    "RiskAssessResponse",
    "PrescriptiveRequest",
    "PrescriptiveResponse",
    "ScenarioSimulateRequest",
    "ScenarioSimulateResponse",
    "ExplainRequest",
    "ExplainResponse",
]
