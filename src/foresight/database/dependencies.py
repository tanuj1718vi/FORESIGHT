"""FastAPI database dependencies."""

from collections.abc import Generator
from sqlalchemy.orm import Session
from foresight.database.session import get_db

__all__ = ["get_db"]
