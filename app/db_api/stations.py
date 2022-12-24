from pydantic import BaseModel, Field, parse_obj_as

from app.db_api.client import client


class Station(BaseModel):
    name: str = Field(..., alias="value")
    id: str
    weight: int
    type: str = Field(..., alias='typeStr')


def fetch_stations(name: str, limit=10) -> list[Station]:
    return parse_obj_as(list[Station], client.stations(name, limit))
