import typing as t
from datetime import datetime

from fastapi import APIRouter

from app import db_api
from app.schemas import bahn as schemas

router = APIRouter()


@router.get("/stations", response_model=schemas.ReadStationsResponse)
def read_stations(name: str) -> schemas.ReadStationsResponse:
    return schemas.ReadStationsResponse(
        stations=[schemas.Station.from_db_api(s) for s in db_api.fetch_stations(name)],
    )


@router.get("/connections", response_model=schemas.ReadConnectionsResponse)
def read_connections(
    origin: str,
    destination: str,
    departure: t.Optional[datetime] = None,
) -> schemas.ReadConnectionsResponse:
    return schemas.ReadConnectionsResponse(
        connections=[
            schemas.Connection.from_db_api(c)
            for c in db_api.fetch_connections(origin, destination, departure)
        ],
    )
