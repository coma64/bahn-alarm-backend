"""
Minimal FastAPI application taken directly from the tutorial.
https://fastapi.tiangolo.com/
"""

from fastapi import FastAPI

from app.database import init_tortoise
from app.routers import bahn

app = FastAPI()
init_tortoise(app)

app.include_router(bahn.router)
