"""
Minimal FastAPI application taken directly from the tutorial.
https://fastapi.tiangolo.com/
"""

import typing as t
from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel

from .db_api.stations import Station, fetch_stations
from .db_api.connections import Connection, fetch_connections
from .register_tortoise import configure_tortoise

app = FastAPI()
configure_tortoise(app)


@app.get("/stations")
def read_stations(name: str) -> list[Station]:
    return fetch_stations(name)


@app.get("/connections")
def read_connections(
    origin: str, destination: str, departure: t.Optional[datetime] = None
) -> list[Connection]:
    return fetch_connections(origin, destination, departure)
