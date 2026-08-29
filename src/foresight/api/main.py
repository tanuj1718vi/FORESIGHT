"""Main FastAPI enterprise application entrypoint for Project FORESIGHT."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from foresight.api.routers import (
    data_views_router,
    explain_router,
    forecast_router,
    health_router,
    inventory_router,
    risk_router,
)
from foresight.api.schemas.common import ErrorResponse
from foresight.config.constants import MODELS_DIR
from foresight.forecasting.base import BaseForecaster
from foresight.utils.exceptions import ForesightError
from foresight.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager pre-warming champion and quantile models at startup."""
    logger.info("Initializing FORESIGHT Enterprise Intelligence Service...")
    champ_path = MODELS_DIR / "champion_forecaster.pkl"
    if champ_path.exists():
        try:
            model = BaseForecaster.load(champ_path)
            logger.info(f"Successfully loaded champion model '{model.name}' at startup.")
        except Exception as e:
            logger.error(f"Failed to load champion model: {e}")
    else:
        logger.warning(f"Champion model not found at {champ_path}")
    yield
    logger.info("Shutting down FORESIGHT Enterprise Intelligence Service...")


def create_app() -> FastAPI:
    """FastAPI application factory."""
    app = FastAPI(
        title="FORESIGHT — Demand & Inventory Intelligence Service",
        description="Production REST microservice for AI-powered demand forecasting, multi-echelon inventory optimization, and supply chain risk intelligence.",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception Handlers
    @app.exception_handler(ForesightError)
    async def foresight_exception_handler(request: Request, exc: ForesightError) -> JSONResponse:
        logger.error(f"Domain Exception on {request.url}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(
                error_code="DOMAIN_VALIDATION_ERROR",
                message=str(exc),
                details=exc.details or {},
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(f"Unhandled Exception on {request.url}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error_code="INTERNAL_SERVER_ERROR",
                message="An unexpected internal server error occurred.",
                details={"error": str(exc)},
            ).model_dump(),
        )

    # Mount Routers
    app.include_router(health_router)
    app.include_router(forecast_router)
    app.include_router(inventory_router)
    app.include_router(risk_router)
    app.include_router(explain_router)
    app.include_router(data_views_router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("foresight.api.main:app", host="0.0.0.0", port=8000, reload=True)
