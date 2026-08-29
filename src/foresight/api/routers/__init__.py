"""FastAPI API routers package."""

from foresight.api.routers.data_views import router as data_views_router
from foresight.api.routers.explain import router as explain_router
from foresight.api.routers.forecast import router as forecast_router
from foresight.api.routers.health import router as health_router
from foresight.api.routers.inventory import router as inventory_router
from foresight.api.routers.risk import router as risk_router

__all__ = [
    "health_router",
    "forecast_router",
    "inventory_router",
    "risk_router",
    "explain_router",
    "data_views_router",
]
