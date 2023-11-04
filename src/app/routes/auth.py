from typing import Sequence, Annotated

from fastapi import Depends, status, HTTPException, Request
from fastapi.routing import APIRoute
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from starlette.responses import RedirectResponse, HTMLResponse
import structlog

from app.models.users import Users

from app import utils
from app.config.config import settings
from app.crud.users import user
from app.oauth import get_current_user, create_access_token
from app.template import templates


logger: structlog.stdlib.BoundLogger = structlog.getLogger(__name__)


async def get_login(request: Request):
    return templates.TemplateResponse(
        "views/login.html", context={"request": request}
    )


async def login(
    request: Request,
    user_credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    auth_user = await user.get_by_email(user_credentials.username)
    if not auth_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials",
        )

    if not utils.verify(user_credentials.password, auth_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials",
        )

    access_token = create_access_token(data={"user_id": str(auth_user.id)})

    response = RedirectResponse(
        request.url_for("dashboard"), status_code=status.HTTP_303_SEE_OTHER
    )
    response.set_cookie(
        key="token",
        value=access_token,
        expires=settings.access_token_expire_minutes * 60,
        domain=settings.url_base,
        httponly=True,
        secure=True,
    )
    return response


async def route_logout_and_remove_cookie():
    response = RedirectResponse(url="", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="token", domain=settings.url_base)
    return response


def read_user_me(current_user: Users = Depends(get_current_user)):
    return current_user


def forgot_password(req: Request):
    body = req.query_params
    email = body.get("email", None)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Must give email"
        )

    forgotten_user = user.get_by_email(email=email)
    if not forgotten_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"User not found"
        )

    return forgotten_user.__dict__


def update_password(current_user: Users = Depends(get_current_user)):
    pass


def auth_routes() -> Sequence[APIRoute]:
    return [
        APIRoute(
            path="/",
            endpoint=login,
            methods=["POST"],
            response_class=RedirectResponse,
        ),
        APIRoute(
            path="/",
            endpoint=get_login,
            methods=["GET"],
            response_class=HTMLResponse,
        ),
    ]
