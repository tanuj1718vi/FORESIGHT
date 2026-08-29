"""Unit tests for configuration loading, merging, and environment overrides."""

import os
from pathlib import Path

import pytest

from foresight.config.constants import Environment
from foresight.config.settings import Settings, _deep_merge, _load_yaml, get_settings


@pytest.mark.unit
def test_default_settings_initialization() -> None:
    """Verify Settings initializes with valid default values when no config files are provided."""
    settings = Settings()
    assert settings.app.name == "FORESIGHT"
    assert settings.app.version == "0.1.0"
    assert settings.data.default_lead_time_days == 7
    assert settings.forecasting.default_horizon_days == 30
    assert settings.inventory.default_service_level == 0.95
    assert settings.env == Environment.DEVELOPMENT


@pytest.mark.unit
def test_deep_merge_utility() -> None:
    """Verify recursive dictionary merge correctly overrides nested keys while keeping others."""
    base = {
        "app": {"name": "BaseApp", "debug": False, "nested": {"k1": "v1"}},
        "data": {"limit": 100},
    }
    override = {
        "app": {"debug": True, "nested": {"k2": "v2"}},
        "data": {"limit": 200},
        "new_key": "val",
    }
    merged = _deep_merge(base, override)

    assert merged["app"]["name"] == "BaseApp"
    assert merged["app"]["debug"] is True
    assert merged["app"]["nested"] == {"k1": "v1", "k2": "v2"}
    assert merged["data"]["limit"] == 200
    assert merged["new_key"] == "val"


@pytest.mark.unit
def test_load_yaml_missing_file(tmp_path: Path) -> None:
    """Verify _load_yaml returns empty dict when file does not exist."""
    non_existent = tmp_path / "does_not_exist.yaml"
    result = _load_yaml(non_existent)
    assert result == {}


@pytest.mark.unit
def test_settings_load_from_yaml(temp_config_dir: Path) -> None:
    """Verify Settings.load properly combines base and environment YAMLs."""
    settings = Settings.load(config_dir=temp_config_dir, env="development")

    # Values from base.yaml
    assert settings.app.name == "FORESIGHT-TEST"
    assert settings.data.date_column == "test_date"
    assert settings.data.sku_column == "test_sku"
    assert settings.inventory.default_service_level == 0.98

    # Overridden values from environments/development.yaml
    assert settings.app.debug is False
    assert settings.forecasting.backtest_splits == 5


@pytest.mark.unit
def test_settings_env_var_override(clean_env: None, temp_config_dir: Path) -> None:
    """Verify environment variables override both defaults and YAML configurations."""
    os.environ["FORESIGHT_APP__NAME"] = "FORESIGHT-OVERRIDDEN"
    os.environ["FORESIGHT_API_PORT"] = "9999"

    settings = Settings.load(config_dir=temp_config_dir, env="development")
    assert settings.app.name == "FORESIGHT-OVERRIDDEN"
    assert settings.api_port == 9999


@pytest.mark.unit
def test_get_settings_cached() -> None:
    """Verify get_settings returns a singleton cached Settings object."""
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2
