import dramatiq
from dramatiq.brokers.redis import RedisBroker
from periodiq import PeriodiqMiddleware

from app import database, settings


def configure() -> None:
    broker = RedisBroker(host=settings.redis_host)
    broker.add_middleware(database.TortoiseDramatiqMiddleware())
    broker.add_middleware(PeriodiqMiddleware(skip_delay=30))
    dramatiq.set_broker(broker)
