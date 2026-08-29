"""Path constants and foundational domain enumerations for Project FORESIGHT."""

from enum import Enum
from pathlib import Path

# Base Paths
PACKAGE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = PACKAGE_DIR.parent
ROOT_DIR = SRC_DIR.parent

# Storage and Artifact Paths
CONFIGS_DIR = ROOT_DIR / "configs"
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"
MODELS_DIR = ROOT_DIR / "models"
LOGS_DIR = ROOT_DIR / "logs"
NOTEBOOKS_DIR = ROOT_DIR / "notebooks"
DOCS_DIR = ROOT_DIR / "docs"
REPORTS_DIR = ROOT_DIR / "reports"
DATABASE_DIR = ROOT_DIR / "database"


class Environment(str, Enum):
    """Runtime environment modes."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class RiskLevel(str, Enum):
    """Inventory risk classification levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RecommendationAction(str, Enum):
    """Prescriptive inventory actions."""
    ORDER = "ORDER"
    HOLD = "HOLD"
    REDUCE = "REDUCE"
    EXPEDITE = "EXPEDITE"
    MONITOR = "MONITOR"
    REBALANCE = "REBALANCE"


class RecommendationUrgency(str, Enum):
    """Priority urgency for inventory actions."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ForecastMetric(str, Enum):
    """Standard forecast evaluation metrics."""
    MAE = "mae"
    RMSE = "rmse"
    WAPE = "wape"
    SMAPE = "smape"
    MAPE = "mape"
    MASE = "mase"
