import asyncio
import logging
import time
from decimal import Decimal

from app.core.config import get_settings
from app.domain.repositories import PriceRepository
from app.infrastructure.database import Database
from app.infrastructure.deribit.client import DeribitClient, DeribitClientError
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


async def _fetch_prices(
    base_url: str,
    tickers: list[str],
) -> list[tuple[str, Decimal]]:
    results: list[tuple[str, Decimal]] = []
    async with DeribitClient(base_url=base_url) as client:
        for ticker in tickers:
            price = await client.get_index_price(ticker)
            results.append((ticker, price))
    return results


@celery_app.task(
    name="app.workers.tasks.fetch_and_store_prices",
    bind=True,
    max_retries=3,
    default_retry_delay=15,
)
def fetch_and_store_prices(self) -> dict[str, str]:
    settings = get_settings()
    timestamp = int(time.time())

    try:
        fetched = asyncio.run(
            _fetch_prices(settings.deribit_base_url, settings.ticker_list)
        )
    except (DeribitClientError, OSError, TimeoutError) as exc:
        logger.exception("Failed to fetch prices from Deribit")
        raise self.retry(exc=exc) from exc

    database = Database(settings)
    items = [(ticker, price, timestamp) for ticker, price in fetched]

    with database.session_scope() as session:
        repository = PriceRepository(session)
        repository.save_many(items)

    logger.info("Stored %s price ticks at %s", len(items), timestamp)
    return {ticker: str(price) for ticker, price in fetched}
