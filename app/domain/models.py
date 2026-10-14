from decimal import Decimal

from sqlalchemy import BigInteger, Index, Numeric, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class PriceTick(Base):
    """Stored index price snapshot for a currency ticker."""

    __tablename__ = "price_ticks"
    __table_args__ = (
        Index("ix_price_ticks_ticker_timestamp", "ticker", "timestamp"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(String(32), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(24, 8), nullable=False)
    timestamp: Mapped[int] = mapped_column(BigInteger, nullable=False)

    def __repr__(self) -> str:
        return (
            f"PriceTick(id={self.id!r}, ticker={self.ticker!r}, "
            f"price={self.price!r}, timestamp={self.timestamp!r})"
        )
