from datetime import datetime, UTC

from beanie import Document
from pydantic import Field


class Item(Document):
    class Settings:
        name = "items"

    created_date: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))

    cost: float
    name: str
    description: str
    quantity: int
