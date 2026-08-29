"""Health, readiness, and version API endpoints."""

from fastapi import APIRouter

from foresight.api.schemas.common import HealthResponse, ReadinessResponse, VersionResponse
from foresight.config.constants import MODELS_DIR, PROCESSED_DATA_DIR

router = APIRouter(tags=["Health & Governance"])


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Liveness probe to confirm service is running."""
    return HealthResponse()


@router.get("/readiness", response_model=ReadinessResponse)
def get_readiness() -> ReadinessResponse:
    """Readiness probe checking availability of serialized artifacts."""
    champ_exists = (MODELS_DIR / "champion_forecaster.pkl").exists()
    quant_exists = (MODELS_DIR / "quantile_forecaster.pkl").exists()
    feat_exists = (PROCESSED_DATA_DIR / "features_engineered.parquet").exists()

    all_ready = champ_exists and quant_exists and feat_exists
    return ReadinessResponse(
        status="ready" if all_ready else "degraded",
        champion_model_loaded=champ_exists,
        quantile_model_loaded=quant_exists,
        features_loaded=feat_exists,
    )


@router.get("/version", response_model=VersionResponse)
def get_version() -> VersionResponse:
    """Return API version, build information, and registered models."""
    return VersionResponse(
        service_name="FORESIGHT Demand Intelligence Service",
        version="1.0.0",
        environment="production",
        models={
            "champion_forecaster": "XGBoost",
            "quantile_forecaster": "Quantile Gradient Boosting (P10, P50, P90)",
            "safety_stock_engine": "Combined Uncertainty (Z * sqrt(L*var_d + d^2*var_L))",
            "explainability_engine": "TreeSHAP",
        },
    )
