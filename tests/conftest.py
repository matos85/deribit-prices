from collections.abc import Generator
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_session
from app.core.config import Settings
from app.domain.models import Base
from app.domain.repositories import PriceRepository
from app.main import create_app


@pytest.fixture
def settings() -> Settings:
    return Settings(
        DATABASE_URL="sqlite+pysqlite:///:memory:",
        REDIS_URL="redis://localhost:6379/0",
        DERIBIT_BASE_URL="https://www.deribit.com/api/v2",
        TICKERS="btc_usd,eth_usd",
    )


@pytest.fixture
def db_session(settings: Settings) -> Generator[Session, None, None]:
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def repository(db_session: Session) -> PriceRepository:
    return PriceRepository(db_session)


@pytest.fixture
def seeded_repository(repository: PriceRepository, db_session: Session) -> PriceRepository:
    repository.save("btc_usd", Decimal("65000.12"), 1_700_000_000)
    repository.save("btc_usd", Decimal("65100.50"), 1_700_000_060)
    repository.save("btc_usd", Decimal("65200.00"), 1_700_000_120)
    repository.save("eth_usd", Decimal("3500.10"), 1_700_000_000)
    db_session.commit()
    return repository


@pytest.fixture
def client(db_session: Session, settings: Settings) -> Generator[TestClient, None, None]:
    application = create_app(settings)

    def override_get_session() -> Generator[Session, None, None]:
        try:
            yield db_session
            db_session.commit()
        except Exception:
            db_session.rollback()
            raise

    application.dependency_overrides[get_session] = override_get_session

    with TestClient(application) as test_client:
        yield test_client

    application.dependency_overrides.clear()
