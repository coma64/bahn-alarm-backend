from datetime import datetime, timedelta

import dramatiq
import structlog
from dramatiq.brokers.redis import RedisBroker

from app import models, db_api, database, settings
from app.tasks.run_async import INSIDE_DRAMATIQ, event_loop, run_async

log = structlog.stdlib.get_logger()

broker = RedisBroker(host=settings.redis_host)
broker.add_middleware(database.TortoiseMiddleware(event_loop))
dramatiq.set_broker(broker)

if INSIDE_DRAMATIQ:
    event_loop.run_until_complete(database.init_tortoise_dramatiq())


@dramatiq.actor(max_retries=0)
@run_async
async def fetch_connection_delay_info(tracked_connection_id: int) -> None:
    tracked_conn = await models.TrackedConnection.get_or_none(pk=tracked_connection_id)
    assert tracked_conn, f"{tracked_connection_id=} doesn't exist"

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
