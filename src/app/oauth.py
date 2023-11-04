from datetime import datetime, timedelta
from typing import Optional

import structlog.stdlib
from fastapi import Depends, status, HTTPException, Cookie, Request
from fastapi.security import OAuth2PasswordBearer

from jose import JWTError, jwt

from app.config.config import settings
from app.crud.users import user as user_crud
from app.models.users import Users
from app.schemas.users import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")
logger = structlog.stdlib.get_logger(__name__)

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(id=user_id)
    except JWTError:
        raise credentials_exception

    return token_data


async def get_cookie_token(request: Request):
    header_token = request.cookies.get("token")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = verify_access_token(header_token, credentials_exception)

    return await user_crud.get_one(token.id)


async def get_current_user(
    request: Request,
    header_token: Optional[str] = Depends(oauth2_scheme),
    token: Optional[str] = Cookie(default=None),
):
    logger.debug("Token", token=token, request=request)
    logger.debug("Hi")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = verify_access_token(header_token, credentials_exception)
    auth_user = await user_crud.get_one(token.id)

    return auth_user


def get_current_active_user(
    current_user: Users = Depends(get_current_user),
) -> Users:
    if not user_crud.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_superuser(
    current_user: Users = Depends(get_current_user),
) -> Users:
    if not user_crud.is_admin(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user
