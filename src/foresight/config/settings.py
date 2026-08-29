"""Application configuration and settings management for Project FORESIGHT."""

from functools import lru_cache
from pathlib import Path
from typing import Any, ClassVar

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from foresight.config.constants import CONFIGS_DIR, Environment


def _load_yaml(file_path: Path) -> dict[str, Any]:
    """Safely load and parse a YAML file if it exists."""
    if not file_path.is_file():
        return {}
    with open(file_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data if isinstance(data, dict) else {}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge two dictionaries."""
    merged = base.copy()
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


class YamlDictSettingsSource(PydanticBaseSettingsSource):
    """Custom settings source that injects merged YAML file configurations."""

    def __init__(self, settings_cls: type[BaseSettings], yaml_data: dict[str, Any]) -> None:
        super().__init__(settings_cls)
        self.yaml_data = yaml_data

    def get_field_value(self, field: Any, field_name: str) -> tuple[Any, str, bool]:
        value = self.yaml_data.get(field_name)
        return value, field_name, False

    def __call__(self) -> dict[str, Any]:
        return self.yaml_data


class AppSettings(BaseModel):
    """General application metadata and behavior."""
    name: str = "FORESIGHT"
    version: str = "0.1.0"
    description: str = "AI-Powered Demand Forecasting & Inventory Intelligence Platform"
    timezone: str = "UTC"
    debug: bool = False


class DataSettings(BaseModel):
    """Data schema column names and ingestion constraints."""
    date_column: str = "date"
    sku_column: str = "sku_id"
    target_column: str = "quantity"
    category_column: str = "category"
    store_column: str = "store_id"
    price_column: str = "price"
    inventory_column: str = "inventory_level"
    lead_time_column: str = "lead_time_days"
    promotion_column: str = "is_promoted"
    default_lead_time_days: int = 7
    history_days_required: int = 90


class FeatureSettings(BaseModel):
    """Feature engineering pipeline parameters."""
    lags: list[int] = Field(default_factory=lambda: [1, 7, 14, 21, 28, 56])
    rolling_windows: list[int] = Field(default_factory=lambda: [7, 14, 28])
    rolling_metrics: list[str] = Field(default_factory=lambda: ["mean", "std", "min", "max"])
    calendar_features: list[str] = Field(
        default_factory=lambda: [
            "day_of_week",
            "day_of_month",
            "week_of_year",
            "month",
            "quarter",
            "year",
            "is_weekend",
        ]
    )
    include_holidays: bool = True


class ForecastingSettings(BaseModel):
    """Demand forecasting hyperparameters and backtesting setup."""
    default_horizon_days: int = 30
    backtest_splits: int = 4
    backtest_step_days: int = 14
    primary_metric: str = "wape"
    models: list[str] = Field(
        default_factory=lambda: [
            "naive",
            "seasonal_naive",
            "moving_average",
            "linear_regression",
            "random_forest",
            "xgboost",
        ]
    )
    confidence_intervals: list[float] = Field(default_factory=lambda: [0.10, 0.50, 0.90])


class InventorySettings(BaseModel):
    """Inventory optimization parameters and thresholds."""
    default_service_level: float = 0.95
    holding_cost_annual_rate: float = 0.20
    ordering_cost_fixed: float = 50.0
    working_days_per_year: int = 365
    days_of_supply_low_threshold: int = 7
    days_of_supply_high_threshold: int = 45


class StockoutThresholds(BaseModel):
    """Threshold boundaries for stockout risk scoring."""
    low: float = 0.25
    medium: float = 0.50
    high: float = 0.75


class RiskSettings(BaseModel):
    """Inventory risk engine scoring thresholds."""
    stockout_thresholds: StockoutThresholds = Field(default_factory=StockoutThresholds)
    overstock_threshold_days: int = 60


class LoggingSettings(BaseModel):
    """Logging subsystem configuration."""
    level: str = "INFO"
    format: str = "standard"  # standard or json
    log_to_file: bool = True
    log_dir: str = "logs"
    log_file_name: str = "foresight.log"


class Settings(BaseSettings):
    """Top-level unified system settings for FORESIGHT."""

    model_config = SettingsConfigDict(
        env_prefix="FORESIGHT_",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    _active_yaml_data: ClassVar[dict[str, Any]] = {}

    env: Environment = Environment.DEVELOPMENT

    # Sub-component configs
    app: AppSettings = Field(default_factory=AppSettings)
    data: DataSettings = Field(default_factory=DataSettings)
    features: FeatureSettings = Field(default_factory=FeatureSettings)
    forecasting: ForecastingSettings = Field(default_factory=ForecastingSettings)
    inventory: InventorySettings = Field(default_factory=InventorySettings)
    risk: RiskSettings = Field(default_factory=RiskSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)

    # Database & Storage
    database_url: str = "sqlite:///./database/foresight.db"

    # MLflow
    mlflow_tracking_uri: str = "sqlite:///./mlflow.db"
    mlflow_experiment_name: str = "foresight_demand_forecast"

    # API & Dashboard
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    streamlit_port: int = 8501

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        yaml_source = YamlDictSettingsSource(settings_cls, cls._active_yaml_data)
        # Precedence: init kwargs > env vars > .env > yaml configs > defaults
        return (init_settings, env_settings, dotenv_settings, yaml_source, file_secret_settings)

    @classmethod
    def load(cls, config_dir: Path = CONFIGS_DIR, env: str | None = None, **kwargs: Any) -> "Settings":
        """Load settings from base YAML, environment YAML, and environment variables."""
        base_yaml = _load_yaml(config_dir / "base.yaml")

        # Determine target environment
        target_env = env or base_yaml.get("env", Environment.DEVELOPMENT.value)
        env_yaml_path = config_dir / "environments" / f"{target_env}.yaml"
        env_yaml = _load_yaml(env_yaml_path)

        merged = _deep_merge(base_yaml, env_yaml)
        if "env" not in merged:
            merged["env"] = target_env

        cls._active_yaml_data = merged
        return cls(**kwargs)


@lru_cache
def get_settings() -> Settings:
    """Return a cached global Settings instance."""
    return Settings.load()
