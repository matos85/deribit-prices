from decimal import Decimal

import pytest
from aioresponses import aioresponses

from app.infrastructure.deribit.client import DeribitClient, DeribitClientError


@pytest.mark.asyncio
async def test_get_index_price_success() -> None:
    base_url = "https://www.deribit.com/api/v2"
    with aioresponses() as mocked:
        mocked.get(
            f"{base_url}/public/get_index_price?index_name=btc_usd",
            payload={"jsonrpc": "2.0", "result": {"index_price": 65123.45}, "id": None},
        )
        async with DeribitClient(base_url=base_url) as client:
            price = await client.get_index_price("btc_usd")

    assert price == Decimal("65123.45")


@pytest.mark.asyncio
async def test_get_index_price_api_error() -> None:
    base_url = "https://www.deribit.com/api/v2"
    with aioresponses() as mocked:
        mocked.get(
            f"{base_url}/public/get_index_price?index_name=btc_usd",
            payload={"jsonrpc": "2.0", "error": {"message": "bad request"}, "id": None},
        )
        async with DeribitClient(base_url=base_url) as client:
            with pytest.raises(DeribitClientError):
                await client.get_index_price("btc_usd")


@pytest.mark.asyncio
async def test_get_index_price_unexpected_payload() -> None:
    base_url = "https://www.deribit.com/api/v2"
    with aioresponses() as mocked:
        mocked.get(
            f"{base_url}/public/get_index_price?index_name=eth_usd",
            payload={"jsonrpc": "2.0", "result": {}, "id": None},
        )
        async with DeribitClient(base_url=base_url) as client:
            with pytest.raises(DeribitClientError):
                await client.get_index_price("eth_usd")
