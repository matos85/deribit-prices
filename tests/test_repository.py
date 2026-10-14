from decimal import Decimal

from app.domain.repositories import PriceRepository


def test_list_by_ticker_returns_sorted_ticks(seeded_repository: PriceRepository) -> None:
    ticks = seeded_repository.list_by_ticker("btc_usd")

    assert len(ticks) == 3
    assert [tick.timestamp for tick in ticks] == [1_700_000_000, 1_700_000_060, 1_700_000_120]
    assert ticks[0].price == Decimal("65000.12")


def test_get_latest_returns_newest_tick(seeded_repository: PriceRepository) -> None:
    tick = seeded_repository.get_latest("btc_usd")

    assert tick is not None
    assert tick.timestamp == 1_700_000_120
    assert tick.price == Decimal("65200.00")


def test_get_latest_returns_none_when_empty(repository: PriceRepository) -> None:
    assert repository.get_latest("btc_usd") is None


def test_list_by_ticker_and_period_filters_inclusive(
    seeded_repository: PriceRepository,
) -> None:
    ticks = seeded_repository.list_by_ticker_and_period(
        "btc_usd",
        date_from=1_700_000_060,
        date_to=1_700_000_120,
    )

    assert len(ticks) == 2
    assert [tick.timestamp for tick in ticks] == [1_700_000_060, 1_700_000_120]
