import re
import typing as t
from datetime import datetime, timedelta

from pydantic import BaseModel, Field, PrivateAttr, parse_obj_as, validator

from app import models
from app.db_api.client import client

BAHN_TIME_REGEX = re.compile(r"(?P<hours>\d\d?):(?P<minutes>\d\d)")


def parse_bahn_time(target_type: t.Type) -> t.Callable[[str], t.Any]:
    def validator(value: str) -> t.Any:
        matches = BAHN_TIME_REGEX.match(value)
        assert (
            matches
        ), f"time field {value=} doesn't match regex {BAHN_TIME_REGEX.pattern=}"

        try:
            hours = int(matches.group("hours"))
            minutes = int(matches.group("minutes"))
        except ValueError as e:
            raise ValueError(f"time {value=} cannot be converted to an int") from e

        return target_type(hours=hours, minutes=minutes)

    return validator


class BahnTime(BaseModel):
    hours: int
    minutes: int


class Delay(BaseModel):
    delay_departure_minutes: int = Field(0, alias="delay_departure")
    delay_arrival_minutes: int = Field(0, alias="delay_arrival")


class Connection(BaseModel):
    departure: BahnTime
    arrival: BahnTime
    duration: timedelta = Field(..., alias="time")
    is_on_time: bool = Field(..., alias="ontime")
    is_canceled: bool = Field(..., alias="canceled")
    delay: Delay = Field(Delay)

    parse_departure = validator("departure", pre=True, allow_reuse=True)(
        parse_bahn_time(BahnTime)
    )
    parse_arrival = validator("arrival", pre=True, allow_reuse=True)(
        parse_bahn_time(BahnTime)
    )
    parse_duration = validator("duration", pre=True, allow_reuse=True)(
        parse_bahn_time(timedelta)
    )


# TODO: make async
def fetch_connections(
    origin: str,
    destination: str,
    departure: t.Optional[datetime] = None,
) -> list[Connection]:
    return parse_obj_as(
        list[Connection],
        client.connections(origin, destination, departure or datetime.now()),
    )


def get_matching_connection(
    connections: list[Connection],
    tracked_connection: models.TrackedConnection,
) -> Connection | None:
    return next(
        (
            c
            for c in connections
            if (
                c.departure.hours == tracked_connection.hours
                and c.departure.minutes == tracked_connection.minutes
            )
        ),
        None,
    )
