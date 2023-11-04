import structlog.stdlib
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRoute


from app.template import templates

logger = structlog.stdlib.get_logger(__name__)


async def get_dashboard(
    request: Request,
):
    return templates.TemplateResponse(
        "views/dashboard.html", context={"request": request}
    )


def dashboard_routes() -> list[APIRoute]:
    return [
        APIRoute(
            path="/",
            name="dashboard",
            endpoint=get_dashboard,
            response_class=HTMLResponse,
        ),
    ]
