from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.routing import APIRoute, Mount


from app.database.init_db import connect_to_mongo, close_mongo_connection
from app.config.logging import setup_logging, setup_fastapi

from app.routes.auth import auth_routes
from app.routes.dashaboard import get_dashboard


@asynccontextmanager
async def lifespan(fast_app: FastAPI):
    db_client = await connect_to_mongo()
    yield
    await close_mongo_connection()


setup_logging(log_level="DEBUG")

app = FastAPI(
    lifespan=lifespan,
    routes=[
        Mount(
            "/login",
            routes=auth_routes()
        ),
        APIRoute(
            path="/dashboard",
            name="dashboard",
            endpoint=get_dashboard,
            response_class=HTMLResponse,
        ),
    ],
)
setup_fastapi(app)
