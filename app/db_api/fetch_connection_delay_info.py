from datetime import datetime, timedelta

import structlog

from app import db_api, models

log = structlog.stdlib.get_logger()


async def fetch_connection_delay_info(
    tracked_conn: models.TrackedConnection,
) -> (bool, int):
    log.info(
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
        log.info("No matching connection found", departure=departure.isoformat())
        return False, 0

    log.info("Matching connection found", **match.dict())

    if delay_info := await tracked_conn.delay_info.get_or_none():
        old_delay_minutes = delay_info.delay_departure_minutes

        delay_info.is_on_time = match.is_on_time
        delay_info.is_canceled = match.is_canceled
        delay_info.delay_departure_minutes = (
            match.delay.delay_departure_minutes if match.delay else 0
        )
        delay_info.delay_arrival_minutes = (
            match.delay.delay_arrival_minutes if match.delay else 0
        )

        new_delay_minutes = delay_info.delay_departure_minutes
        await delay_info.save()
    else:
        old_delay_minutes = 0
        new_delay_minutes = match.delay.delay_departure_minutes if match.delay else 0

        await models.ConnectionDelayInfo.create(
            tracked_connection=tracked_conn,
            is_on_time=match.is_on_time,
            is_canceled=match.is_canceled,
            delay_departure_minutes=(
                match.delay.delay_departure_minutes if match.delay else 0
            ),
            delay_arrival_minutes=(
                match.delay.delay_arrival_minutes if match.delay else 0
            ),
        )

    return new_delay_minutes != old_delay_minutes, new_delay_minutes
