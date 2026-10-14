from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.models import PriceTick


class PriceRepository:
    """Persistence operations for price ticks."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, ticker: str, price: Decimal, timestamp: int) -> PriceTick:
        tick = PriceTick(ticker=ticker, price=price, timestamp=timestamp)
        self._session.add(tick)
        self._session.flush()
        return tick

    def save_many(
        self,
        items: list[tuple[str, Decimal, int]],
    ) -> list[PriceTick]:
        ticks = [
            PriceTick(ticker=ticker, price=price, timestamp=timestamp)
            for ticker, price, timestamp in items
        ]
        self._session.add_all(ticks)
        self._session.flush()
        return ticks

    def list_by_ticker(self, ticker: str) -> list[PriceTick]:
        statement = (
            select(PriceTick)
            .where(PriceTick.ticker == ticker)
            .order_by(PriceTick.timestamp.asc())
        )
        return list(self._session.scalars(statement).all())

    def get_latest(self, ticker: str) -> PriceTick | None:
        statement = (
            select(PriceTick)
            .where(PriceTick.ticker == ticker)
            .order_by(PriceTick.timestamp.desc())
            .limit(1)
        )
        return self._session.scalars(statement).first()

    def list_by_ticker_and_period(
        self,
        ticker: str,
        date_from: int,
        date_to: int,
    ) -> list[PriceTick]:
        statement = (
            select(PriceTick)
            .where(
                PriceTick.ticker == ticker,
                PriceTick.timestamp >= date_from,
                PriceTick.timestamp <= date_to,
            )
            .order_by(PriceTick.timestamp.asc())
        )
        return list(self._session.scalars(statement).all())
