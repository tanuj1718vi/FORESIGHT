"""Database layer package for Project FORESIGHT."""

from foresight.database.base import Base, TimestampMixin
from foresight.database.dependencies import get_db
from foresight.database.models import (
    ForecastRecord,
    InventoryRecord,
    ModelRun,
    Product,
    RecommendationRecord,
    RiskAssessmentRecord,
    SalesRecord,
)
from foresight.database.repositories import (
    BaseRepository,
    ForecastRepository,
    InventoryRepository,
    ModelRepository,
    ProductRepository,
    RecommendationRepository,
    RiskRepository,
    SalesRepository,
)
from foresight.database.seeder import seed_database
from foresight.database.session import (
    DATABASE_URL,
    get_engine,
    get_session_factory,
    init_db,
    session_scope,
)

__all__ = [
    "Base",
    "TimestampMixin",
    "DATABASE_URL",
    "get_engine",
    "get_session_factory",
    "get_db",
    "session_scope",
    "init_db",
    "seed_database",
    "Product",
    "SalesRecord",
    "InventoryRecord",
    "ForecastRecord",
    "RiskAssessmentRecord",
    "RecommendationRecord",
    "ModelRun",
    "BaseRepository",
    "ProductRepository",
    "SalesRepository",
    "InventoryRepository",
    "ForecastRepository",
    "RiskRepository",
    "RecommendationRepository",
    "ModelRepository",
]
