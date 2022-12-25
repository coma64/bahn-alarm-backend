import asyncio

from dramatiq.middleware import Middleware
from fastapi import FastAPI
from tortoise import Tortoise, connections
from tortoise.contrib.fastapi import register_tortoise

from app import settings

ORM_SETTINGS = {
    "connections": {"default": settings.db_url},
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}


def init_tortoise_fastapi(app: FastAPI) -> None:
    register_tortoise(app, config=ORM_SETTINGS)


class TortoiseMiddleware(Middleware):
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop

    def before_consumer_thread_shutdown(self, broker, worker):
        self.loop.run_until_complete(connections.close_all(discard=True))


async def init_tortoise_dramatiq() -> None:
    await Tortoise.init(config=ORM_SETTINGS)
