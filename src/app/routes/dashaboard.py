import structlog.stdlib
from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse

from app.template import templates

logger = structlog.stdlib.get_logger(__name__)
router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def get_dashboard(
    request: Request,
):
    return templates.TemplateResponse(
        "views/dashboard.html", context={"request": request}
    )
