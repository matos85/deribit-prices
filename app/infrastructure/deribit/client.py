from decimal import Decimal
from typing import Any

import aiohttp


class DeribitClientError(Exception):
    """Raised when Deribit API returns an error or unexpected payload."""


class DeribitClient:
    """Async HTTP client for Deribit public index price endpoints."""

    def __init__(
        self,
        base_url: str,
        session: aiohttp.ClientSession | None = None,
        timeout_seconds: float = 10.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._owns_session = session is None
        self._session = session
        self._timeout = aiohttp.ClientTimeout(total=timeout_seconds)

    async def __aenter__(self) -> "DeribitClient":
        if self._session is None:
            self._session = aiohttp.ClientSession(timeout=self._timeout)
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        if self._owns_session and self._session is not None:
            await self._session.close()
            self._session = None

    async def get_index_price(self, index_name: str) -> Decimal:
        if self._session is None:
            raise RuntimeError("DeribitClient must be used as an async context manager")

        url = f"{self._base_url}/public/get_index_price"
        async with self._session.get(url, params={"index_name": index_name}) as response:
            response.raise_for_status()
            payload: dict[str, Any] = await response.json()

        if "error" in payload:
            raise DeribitClientError(f"Deribit error for {index_name}: {payload['error']}")

        result = payload.get("result")
        if not isinstance(result, dict) or "index_price" not in result:
            raise DeribitClientError(
                f"Unexpected Deribit response for {index_name}: {payload}"
            )

        return Decimal(str(result["index_price"]))
