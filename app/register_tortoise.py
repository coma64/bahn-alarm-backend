from tortoise.contrib.fastapi import register_tortoise
from fastapi import FastAPI

from .settings import settings

def configure_tortoise(app: FastAPI) -> None:
    register_tortoise(
        app,
        db_url=settings.db_url,
        modules={'models': ['app.models']},
        generate_schemas=settings.development_mode,
        add_exception_handlers=settings.development_mode,
    )
