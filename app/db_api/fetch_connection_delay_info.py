from datetime import datetime, timedelta

import structlog
from pydantic import BaseModel

from app import db_api, models

log = structlog.stdlib.get_logger()


class DelayInfoChanges(BaseModel):
    old_delay_minutes: int = 0
    new_delay_minutes: int = 0

    old_is_canceled: bool = False
    new_is_cancled: bool = False

    @property
    def has_delay_changed(self) -> bool:
        return self.old_delay_minutes != self.new_delay_minutes

    @property
    def delay_minutes(self) -> int:
        return self.new_delay_minutes

    @property
    def has_is_canceled_changed(self):
        return self.old_is_canceled != self.new_is_cancled

    @property
    def is_canceled(self):
        return self.new_is_cancled


async def fetch_connection_delay_info(
    tracked_conn: models.TrackedConnection,
) -> DelayInfoChanges:
    log.debug(
        "Fetching connection delay info",
        **(
            await models.TrackedConnection_Pydantic.from_tortoise_orm(tracked_conn)
        ).dict(),
    )

    # TODO: timezones
    departure = datetime.now().replace(
        hour=tracked_conn.hours, minute=tracked_conn.minutes, second=0, microsecond=0
    )

    if departure < datetime.now():
        # Already passed today, checking for tomorrow
        departure = departure + timedelta(days=1)

    connections = db_api.fetch_connections(
        tracked_conn.origin_station, tracked_conn.destination_station, departure
    )
    match = db_api.get_matching_connection(connections, tracked_conn)
    if not match:
        log.debug("No matching connection found")
        return DelayInfoChanges()

    log.debug("Matching connection found", **match.dict())

    if delay_info := await tracked_conn.delay_info.get_or_none():
        delay_info_changes = DelayInfoChanges(
            old_delay_minutes=delay_info.delay_departure_minutes,
            old_is_canceled=delay_info.is_canceled,
            new_delay_minutes=match.delay.delay_departure_minutes,
            new_is_canceled=match.is_canceled,
        )

        delay_info.is_on_time = match.is_on_time
        delay_info.is_canceled = match.is_canceled
        delay_info.delay_departure_minutes = match.delay.delay_departure_minutes
        delay_info.delay_arrival_minutes = match.delay.delay_arrival_minutes

        new_delay_minutes = delay_info.delay_departure_minutes
        await delay_info.save()
    else:
        delay_info_changes = DelayInfoChanges(
            new_delay_minutes=match.delay.delay_departure_minutes,
            new_is_canceled=match.is_canceled,
        )

        await models.ConnectionDelayInfo.create(
            tracked_connection=tracked_conn,
            is_on_time=match.is_on_time,
            is_canceled=match.is_canceled,
            delay_departure_minutes=match.delay.delay_departure_minutes,
            delay_arrival_minutes=match.delay.delay_arrival_minutes,
        )

    return delay_info_changes
