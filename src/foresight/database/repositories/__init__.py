"""Database repositories package."""

from foresight.database.repositories.base_repository import BaseRepository
from foresight.database.repositories.forecast_repository import ForecastRepository
from foresight.database.repositories.inventory_repository import InventoryRepository
from foresight.database.repositories.model_repository import ModelRepository
from foresight.database.repositories.product_repository import ProductRepository
from foresight.database.repositories.recommendation_repository import RecommendationRepository
from foresight.database.repositories.risk_repository import RiskRepository
from foresight.database.repositories.sales_repository import SalesRepository

__all__ = [
    "BaseRepository",
    "ProductRepository",
    "SalesRepository",
    "InventoryRepository",
    "ForecastRepository",
    "RiskRepository",
    "RecommendationRepository",
    "ModelRepository",
]
