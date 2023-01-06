import asyncio

from dramatiq.middleware import Middleware
from fastapi import FastAPI
from tortoise import Tortoise, connections
from tortoise.contrib.fastapi import register_tortoise
from asgiref.sync import async_to_sync

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

initialized_tortoise = False


def initialize_tortoise_fastapi(app: FastAPI) -> None:
    global initialized_tortoise
    if initialized_tortoise:
        return
    initialized_tortoise = True

    register_tortoise(app, config=ORM_SETTINGS)


async def initialize_tortoise() -> None:
    global initialized_tortoise
    if initialized_tortoise:
        return
    initialized_tortoise = True

    await Tortoise.init(config=ORM_SETTINGS)


async def close_tortoise_connections() -> None:
    await connections.close_all(discard=True)


initialize_tortoise_sync = async_to_sync(initialize_tortoise)
close_tortoise_connections_sync = async_to_sync(close_tortoise_connections)


class TortoiseDramatiqMiddleware(Middleware):
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop

    def before_consumer_thread_shutdown(self, broker, worker):
        close_tortoise_connections_sync()
