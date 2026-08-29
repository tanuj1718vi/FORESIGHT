"""Global pytest fixtures for Project FORESIGHT test suite."""

import os
from collections.abc import Generator
from pathlib import Path
import pytest
import yaml

from foresight.config.settings import Settings


@pytest.fixture
def temp_config_dir(tmp_path: Path) -> Path:
    """Create a temporary configuration directory with base and environment YAML files."""
    config_dir = tmp_path / "configs"
    env_dir = config_dir / "environments"
    env_dir.mkdir(parents=True)

    base_content = {
        "app": {
            "name": "FORESIGHT-TEST",
            "version": "0.1.0-test",
            "debug": True,
        },
        "data": {
            "date_column": "test_date",
            "sku_column": "test_sku",
            "target_column": "test_quantity",
            "default_lead_time_days": 10,
        },
        "forecasting": {
            "default_horizon_days": 14,
            "backtest_splits": 3,
        },
        "inventory": {
            "default_service_level": 0.98,
        },
    }

    dev_content = {
        "app": {
            "debug": False,
        },
        "forecasting": {
            "backtest_splits": 5,
        },
    }

    with open(config_dir / "base.yaml", "w", encoding="utf-8") as f:
        yaml.dump(base_content, f)

    with open(env_dir / "development.yaml", "w", encoding="utf-8") as f:
        yaml.dump(dev_content, f)

    return config_dir


@pytest.fixture
def clean_env() -> Generator[None, None, None]:
    """Isolate environment variables during tests."""
    old_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(old_env)


@pytest.fixture
def sample_settings(temp_config_dir: Path) -> Settings:
    """Provide a valid test Settings instance."""
    return Settings.load(config_dir=temp_config_dir, env="development")
