from datetime import timedelta

from pydantic import BaseModel

from app import db_api


class Station(BaseModel):
    name: str
    id: str
    weight: int
    type: str

    @classmethod
    def from_db_api(cls, station: db_api.Station) -> "Station":
        return cls.parse_obj(station.dict(by_alias=False))


class ReadStationsResponse(BaseModel):
    stations: list[Station]


class Delay(BaseModel):
    delay_departure_minutes: int
    delay_arrival_minutes: int


class Connection(BaseModel):
    departure: db_api.BahnTime
    arrival: db_api.BahnTime
    duration: timedelta
    on_time: bool
    is_canceled: bool
    delay: Delay

    @classmethod
    def from_db_api(cls, connection: db_api.Connection) -> "Connection":
        return cls.parse_obj(connection.dict(by_alias=False))


class ReadConnectionsResponse(BaseModel):
    connections: list[Connection]
