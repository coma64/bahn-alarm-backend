import json

import dramatiq
import structlog
from asgiref.sync import async_to_sync
from more_itertools import chunked
from periodiq import cron
from pywebpush import webpush

from app import database, db_api, models, settings
from app.db_api.fetch_connection_delay_info import DelayInfoChanges
from app.tasks import configure_dramatiq

log = structlog.stdlib.get_logger()

configure_dramatiq.configure()
database.initialize_tortoise_sync()


@dramatiq.actor(max_retries=0)
def send_delay_info_notifications(
    subscription_infos: list[dict],
    connection_id: int,
    message: str,
) -> None:
    for subscription in subscription_infos:
        try:
            webpush(
                subscription,
                json.dumps(
                    {
                        "message": message,
                        "connection_id": connection_id,
                        "type": "connection-delay",
                    }
                ),
                settings.vapid_private_key_path,
                {"sub": settings.push_notification_subject},
            )
        except Exception:
            log.exception(
                "Got exception while sending push notification. Skipping...",
                subscription=subscription,
                connection_id=connection_id,
            )


def build_delay_message(
    connection: models.TrackedConnection, delay_info_changes: DelayInfoChanges
) -> str:
    if delay_info_changes.has_is_canceled_changed:
        if delay_info_changes.is_canceled:
            return f"Canceled, {connection}"
        else:
            return f"No longer canceled, delay {delay_info_changes.delay_minutes}m, {connection}"
    if delay_info_changes.has_delay_changed:
        return f"Delay {delay_info_changes.delay_minutes}m, {connection}"


@dramatiq.actor(max_retries=0)
@async_to_sync
async def fetch_connection_delay_infos(tracked_connection_ids: list[int]) -> None:
    async for connection in models.TrackedConnection.filter(
        pk__in=tracked_connection_ids
    ):
        try:
            delay_info_changes = await db_api.fetch_connection_delay_info(connection)

            if (
                not delay_info_changes.has_delay_changed
                and not delay_info_changes.has_is_canceled_changed
            ):
                continue

            push_notification_subscription = (
                await connection.tracked_by.all().values_list(
                    "push_notifications_subscription__subscription",
                    flat=True,
                )
            )
            send_delay_info_notifications.send(
                push_notification_subscription,
                connection.pk,
                delay_info_changes.dict(),
            )
        except Exception:
            log.exception(
                "Got exception while fetching delay info", connection_id=connection.pk
            )


@dramatiq.actor(max_retries=0, periodic=cron("*/5 * * * *"))
@async_to_sync
async def periodic_fetch_connection_delay_info() -> None:
    dramatiq.group(
        fetch_connection_delay_infos.message(tracked_connections)
        for tracked_connections in chunked(
            await models.TrackedConnection.all().values_list("id", flat=True),
            4,
        )
    ).run()
