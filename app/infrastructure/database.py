from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings
from app.domain.models import Base


class Database:
    """Owns the SQLAlchemy engine and session factory."""

    def __init__(self, settings: Settings) -> None:
        self._engine: Engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,
        )
        self._session_factory = sessionmaker(
            bind=self._engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    @property
    def engine(self) -> Engine:
        return self._engine

    def create_tables(self) -> None:
        Base.metadata.create_all(bind=self._engine)

    def create_session(self) -> Session:
        return self._session_factory()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        session = self.create_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
