from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.core.config import SUPPORTED_TICKERS, Settings, get_settings
from app.domain.repositories import PriceRepository
from app.infrastructure.database import Database


def get_app_settings(request: Request) -> Settings:
    settings = getattr(request.app.state, "settings", None)
    if settings is not None:
        return settings
    return get_settings()


def get_database(request: Request) -> Database:
    database = getattr(request.app.state, "database", None)
    if database is not None:
        return database
    return Database(get_app_settings(request))


def get_session(
    database: Annotated[Database, Depends(get_database)],
) -> Generator[Session, None, None]:
    session = database.create_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_price_repository(
    session: Annotated[Session, Depends(get_session)],
) -> PriceRepository:
    return PriceRepository(session)


def get_ticker(
    ticker: Annotated[
        str,
        Query(
            ...,
            description="Currency ticker, e.g. btc_usd or eth_usd",
            examples=["btc_usd"],
        ),
    ],
) -> str:
    normalized = ticker.strip().lower()
    if normalized not in SUPPORTED_TICKERS:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Unsupported ticker '{ticker}'. "
                f"Allowed values: {', '.join(sorted(SUPPORTED_TICKERS))}"
            ),
        )
    return normalized
