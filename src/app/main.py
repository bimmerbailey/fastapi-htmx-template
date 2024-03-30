from contextlib import asynccontextmanager
from typing import Sequence

from fastapi import FastAPI
import structlog

from app.dependencies.database import connect_to_mongo, close_mongo_connection
from app.config.logging import setup_logging, setup_fastapi
from app.routes.auth import router as auth_rotes
from app.routes.dashaboard import router as dashboard_rotes
from app.config.settings import get_app_settings, AppSettings


@asynccontextmanager
async def lifespan(fast_app: FastAPI):
    db_client = await connect_to_mongo()
    yield
    await close_mongo_connection(db_client)


def init_app(app_settings: AppSettings = get_app_settings()) -> FastAPI:
    log_renderer: Sequence[structlog.types.Processor]
    if app_settings.debug:
        log_renderer = [structlog.dev.ConsoleRenderer()]
    else:
        log_renderer = [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    log_level = "DEBUG" if app_settings.debug else "INFO"
    setup_logging(processors=log_renderer, log_level=log_level)

    app = FastAPI(
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.include_router(auth_rotes)
    app.include_router(dashboard_rotes)
    setup_fastapi(app)
    return app
