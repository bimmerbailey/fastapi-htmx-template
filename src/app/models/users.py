from datetime import datetime, UTC
from typing import Optional

import pymongo
from beanie import Document
from pydantic import EmailStr, Field


class User(Document):
    created_date: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr
    password: str
    is_admin: bool = False

    class Settings:
        name = "users"

    @classmethod
    async def get_by_email(cls, email: str) -> Optional["User"]:
        return await cls.find_one({"email": email})
