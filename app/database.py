from tortoise.contrib.fastapi import register_tortoise
from fastapi import FastAPI

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


def init_tortoise(app: FastAPI) -> None:
    register_tortoise(app, config=ORM_SETTINGS)
