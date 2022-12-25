import dramatiq
import structlog
from dramatiq.brokers.redis import RedisBroker
from periodiq import PeriodiqMiddleware, cron
from more_itertools import chunked

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
@run_async
async def fetch_connection_delay_infos(tracked_connection_ids: list[int]) -> None:
    async for connection in models.TrackedConnection.filter(pk__in=tracked_connection_ids):
        await db_api.fetch_connection_delay_info(connection)


@dramatiq.actor(max_retries=0, periodic=cron("*/5 * * * *"))
@run_async
async def periodic_fetch_connection_delay_info() -> None:
    dramatiq.group(chunked(await models.TrackedConnection.all().values_list("id", flat=True), 4))
