from functools import lru_cache
from typing import FrozenSet

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


SUPPORTED_TICKERS: FrozenSet[str] = frozenset({"btc_usd", "eth_usd"})


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    database_url: str = Field(
        default="postgresql+psycopg2://deribit:deribit@localhost:5432/deribit_prices",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    deribit_base_url: str = Field(
        default="https://www.deribit.com/api/v2",
        alias="DERIBIT_BASE_URL",
    )
    tickers: str = Field(default="btc_usd,eth_usd", alias="TICKERS")
    fetch_interval_seconds: int = Field(default=60, alias="FETCH_INTERVAL_SECONDS")

    @property
    def ticker_list(self) -> list[str]:
        return [item.strip() for item in self.tickers.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
