"""Common API request/response schemas and metadata models."""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Liveness probe response model."""
    status: str = Field(default="healthy", json_schema_extra={"example": "healthy"})
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    service: str = "FORESIGHT Enterprise Intelligence API"
    version: str = "1.0.0"


class ReadinessResponse(BaseModel):
    """Readiness probe checking models and dependencies."""
    status: str = Field(default="ready", json_schema_extra={"example": "ready"})
    champion_model_loaded: bool
    quantile_model_loaded: bool
    features_loaded: bool
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class VersionResponse(BaseModel):
    """Service version and build metadata."""
    service_name: str = "FORESIGHT API"
    version: str = "1.0.0"
    environment: str = "production"
    models: dict[str, str] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Standard error response payload."""
    error_code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
