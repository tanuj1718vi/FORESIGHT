"""Generic Base Repository providing standard CRUD operations."""

from typing import Generic, Sequence, TypeVar
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session
from foresight.database.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Base repository class wrapping common SQLAlchemy session query patterns."""

    def __init__(self, model_cls: type[T], session: Session) -> None:
        self.model_cls = model_cls
        self.session = session

    def get_by_id(self, ident: int | str) -> T | None:
        """Fetch a single record by primary key."""
        return self.session.get(self.model_cls, ident)

    def list_all(self, limit: int = 1000, offset: int = 0) -> Sequence[T]:
        """Fetch a paginated list of records."""
        stmt: Select[tuple[T]] = select(self.model_cls).limit(limit).offset(offset)
        return self.session.scalars(stmt).all()

    def count(self) -> int:
        """Count total records in table."""
        stmt = select(func.count()).select_from(self.model_cls)
        return int(self.session.scalar(stmt) or 0)

    def add(self, entity: T) -> T:
        """Add a single entity."""
        self.session.add(entity)
        self.session.flush()
        return entity

    def add_all(self, entities: Sequence[T]) -> None:
        """Bulk add multiple entities."""
        self.session.add_all(entities)
        self.session.flush()

    def delete(self, entity: T) -> None:
        """Delete an entity."""
        self.session.delete(entity)
        self.session.flush()
