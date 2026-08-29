"""Database connection, engine configuration, and session management."""

from contextlib import contextmanager
import os
from pathlib import Path
from typing import Generator
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from foresight.config.constants import ROOT_DIR
from foresight.database.base import Base
from foresight.utils.logger import get_logger

logger = get_logger(__name__)

# Default SQLite database path
DEFAULT_DB_PATH = ROOT_DIR / "database" / "foresight.db"
DEFAULT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Connection string with environment override
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH.resolve().as_posix()}")

_engine: Engine | None = None
_SessionFactory: sessionmaker[Session] | None = None


def get_engine(db_url: str | None = None) -> Engine:
    """Get or create singleton SQLAlchemy Engine."""
    global _engine
    if _engine is None or db_url is not None:
        url = db_url or DATABASE_URL
        connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
        _engine = create_engine(
            url,
            connect_args=connect_args,
            pool_pre_ping=True,
            echo=False,
        )
        logger.info(f"Initialized database engine for: {url}")
    return _engine


def get_session_factory(db_url: str | None = None) -> sessionmaker[Session]:
    """Get or create session factory."""
    global _SessionFactory
    if _SessionFactory is None or db_url is not None:
        engine = get_engine(db_url)
        _SessionFactory = sessionmaker(
            bind=engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )
    return _SessionFactory


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a managed database session."""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def session_scope(db_url: str | None = None) -> Generator[Session, None, None]:
    """Context manager for transactional database operations."""
    factory = get_session_factory(db_url)
    session = factory()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database transaction error: {e}")
        raise
    finally:
        session.close()


def init_db(db_url: str | None = None) -> None:
    """Initialize database schema creating all mapped tables."""
    engine = get_engine(db_url)
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema initialized successfully.")
