from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_price_repository, get_ticker
from app.api.schemas.price import PriceTickResponse
from app.domain.repositories import PriceRepository

router = APIRouter(prefix="/prices", tags=["prices"])


@router.get(
    "",
    response_model=list[PriceTickResponse],
    summary="Get all stored prices for a ticker",
)
def get_all_prices(
    ticker: Annotated[str, Depends(get_ticker)],
    repository: Annotated[PriceRepository, Depends(get_price_repository)],
) -> list[PriceTickResponse]:
    ticks = repository.list_by_ticker(ticker)
    return [PriceTickResponse.model_validate(tick) for tick in ticks]


@router.get(
    "/latest",
    response_model=PriceTickResponse,
    summary="Get the latest stored price for a ticker",
)
def get_latest_price(
    ticker: Annotated[str, Depends(get_ticker)],
    repository: Annotated[PriceRepository, Depends(get_price_repository)],
) -> PriceTickResponse:
    tick = repository.get_latest(ticker)
    if tick is None:
        raise HTTPException(
            status_code=404,
            detail=f"No price data found for ticker '{ticker}'",
        )
    return PriceTickResponse.model_validate(tick)


@router.get(
    "/history",
    response_model=list[PriceTickResponse],
    summary="Get stored prices for a ticker filtered by date range",
)
def get_price_history(
    ticker: Annotated[str, Depends(get_ticker)],
    repository: Annotated[PriceRepository, Depends(get_price_repository)],
    date_from: Annotated[
        int,
        Query(..., description="Start of range as UNIX timestamp (inclusive)"),
    ],
    date_to: Annotated[
        int,
        Query(..., description="End of range as UNIX timestamp (inclusive)"),
    ],
) -> list[PriceTickResponse]:
    if date_from > date_to:
        raise HTTPException(
            status_code=422,
            detail="date_from must be less than or equal to date_to",
        )
    ticks = repository.list_by_ticker_and_period(ticker, date_from, date_to)
    return [PriceTickResponse.model_validate(tick) for tick in ticks]
