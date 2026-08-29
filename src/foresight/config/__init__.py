"""Configuration module for Project FORESIGHT."""

from foresight.config.constants import (
    CONFIGS_DIR,
    DATA_DIR,
    DATABASE_DIR,
    DOCS_DIR,
    EXTERNAL_DATA_DIR,
    LOGS_DIR,
    MODELS_DIR,
    NOTEBOOKS_DIR,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
    ROOT_DIR,
    SRC_DIR,
    Environment,
    ForecastMetric,
    RecommendationAction,
    RecommendationUrgency,
    RiskLevel,
)
from foresight.config.settings import Settings, get_settings

__all__ = [
    "ROOT_DIR",
    "SRC_DIR",
    "CONFIGS_DIR",
    "DATA_DIR",
    "RAW_DATA_DIR",
    "PROCESSED_DATA_DIR",
    "EXTERNAL_DATA_DIR",
    "MODELS_DIR",
    "LOGS_DIR",
    "NOTEBOOKS_DIR",
    "DOCS_DIR",
    "DATABASE_DIR",
    "Environment",
    "RiskLevel",
    "RecommendationAction",
    "RecommendationUrgency",
    "ForecastMetric",
    "Settings",
    "get_settings",
]
