import json

import dramatiq
import structlog
from dramatiq.brokers.redis import RedisBroker
from periodiq import PeriodiqMiddleware, cron
from more_itertools import chunked
from pywebpush import webpush

from app import models, db_api, database, settings
from app.tasks.run_async import INSIDE_DRAMATIQ, event_loop, run_async

log = structlog.stdlib.get_logger()

broker = RedisBroker(host=settings.redis_host)
broker.add_middleware(database.TortoiseMiddleware(event_loop))
broker.add_middleware(PeriodiqMiddleware(skip_delay=30))
dramatiq.set_broker(broker)

if INSIDE_DRAMATIQ:
    event_loop.run_until_complete(database.init_tortoise_dramatiq())


@dramatiq.actor(max_retries=0)
def send_delay_info_notifications(
    subscription_infos: list[dict], message: str, connection_id: int
) -> None:
    for subscription in subscription_infos:
        webpush(
            subscription,
            json.dumps(
                {
                    "message": message,
                    "connection_id": connection_id,
                    "type": "connection-delay",
                }
            ),
            "vapid-keys/private_key.pem",
            {"sub": "mailto:coma64@outlookc.com"},
        )


@dramatiq.actor(max_retries=0)
@run_async
async def fetch_connection_delay_infos(tracked_connection_ids: list[int]) -> None:
    async for connection in models.TrackedConnection.filter(
        pk__in=tracked_connection_ids
    ):
        has_delay_changed, delay_minutes = await db_api.fetch_connection_delay_info(
            connection
        )
        if has_delay_changed:
            push_notification_subscription = (
                await connection.tracked_by.all().values_list(
                    "push_notifications_subscription__subscription", flat=True
                )
            )
            send_delay_info_notifications.send(
                push_notification_subscription,
                f"{delay_minutes}m delay, {connection.origin_station} -> {connection.destination_station}, {connection.hours}:{connection.minutes}h",
                connection.pk,
            )


@dramatiq.actor(max_retries=0, periodic=cron("*/5 * * * *"))
@run_async
async def periodic_fetch_connection_delay_info() -> None:
    dramatiq.group(
        fetch_connection_delay_infos.message(tracked_connections)
        for tracked_connections in chunked(
            await models.TrackedConnection.all().values_list("id", flat=True), 4
        )
    ).run()
