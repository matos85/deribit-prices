from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PriceTickResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ticker: str
    price: Decimal
    timestamp: int = Field(description="UNIX timestamp in seconds")
