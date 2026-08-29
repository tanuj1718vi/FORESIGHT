"""Project FORESIGHT - AI-Powered Demand Forecasting & Inventory Intelligence Platform."""

__version__ = "0.1.0"
__author__ = "Project FORESIGHT Team"

from foresight.config.settings import get_settings
from foresight.utils.logger import get_logger

__all__ = ["__version__", "get_settings", "get_logger"]
