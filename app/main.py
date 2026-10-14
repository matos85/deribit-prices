from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.prices import router as prices_router
from app.core.config import Settings, get_settings
from app.infrastructure.database import Database


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        database = Database(app_settings)
        database.create_tables()
        application.state.database = database
        application.state.settings = app_settings
        yield

    application = FastAPI(
        title="Deribit Price Tracker",
        description=(
            "Stores Deribit index prices for btc_usd and eth_usd "
            "and exposes read-only HTTP API."
        ),
        version="1.0.0",
        lifespan=lifespan,
    )
    application.include_router(prices_router)
    return application


app = create_app()
