from pydantic import BaseModel, Field

from .client import client


class Station(BaseModel):
    name: str = Field(..., alias="value")
    id: str
    weight: int
    typeStr: str


def fetch_stations(name: str, limit=10) -> list[Station]:
    return client.stations(name, limit)
