from datetime import datetime, timedelta

import structlog

from app import models, db_api


log = structlog.stdlib.get_logger()


async def fetch_connection_delay_info(tracked_conn: models.TrackedConnection) -> None:
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
        return

    log.info("Matching connection found", **match.dict())

    if delay_info := await tracked_conn.delay_info.get_or_none():
        delay_info.is_on_time = match.is_on_time
        delay_info.is_canceled = match.is_canceled
        delay_info.delay_departure_minutes = (
            match.delay.delay_departure_minutes if match.delay else 0
        )
        delay_info.delay_arrival_minutes = (
            match.delay.delay_arrival_minutes if match.delay else 0
        )
        await delay_info.save()
    else:
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
