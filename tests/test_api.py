from decimal import Decimal

from fastapi.testclient import TestClient

from app.domain.repositories import PriceRepository


def test_get_all_prices(client: TestClient, seeded_repository: PriceRepository) -> None:
    response = client.get("/prices", params={"ticker": "btc_usd"})

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 3
    assert payload[0]["ticker"] == "btc_usd"
    assert Decimal(payload[0]["price"]) == Decimal("65000.12")


def test_get_latest_price(client: TestClient, seeded_repository: PriceRepository) -> None:
    response = client.get("/prices/latest", params={"ticker": "btc_usd"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["timestamp"] == 1_700_000_120
    assert Decimal(payload["price"]) == Decimal("65200.00")


def test_get_latest_price_not_found(client: TestClient) -> None:
    response = client.get("/prices/latest", params={"ticker": "btc_usd"})

    assert response.status_code == 404


def test_get_price_history(client: TestClient, seeded_repository: PriceRepository) -> None:
    response = client.get(
        "/prices/history",
        params={
            "ticker": "btc_usd",
            "date_from": 1_700_000_060,
            "date_to": 1_700_000_120,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert payload[0]["timestamp"] == 1_700_000_060


def test_ticker_is_required(client: TestClient) -> None:
    response = client.get("/prices")

    assert response.status_code == 422


def test_unsupported_ticker(client: TestClient) -> None:
    response = client.get("/prices", params={"ticker": "doge_usd"})

    assert response.status_code == 422


def test_history_rejects_inverted_range(
    client: TestClient,
    seeded_repository: PriceRepository,
) -> None:
    response = client.get(
        "/prices/history",
        params={
            "ticker": "btc_usd",
            "date_from": 1_700_000_200,
            "date_to": 1_700_000_100,
        },
    )

    assert response.status_code == 422
