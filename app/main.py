"""
Minimal FastAPI application taken directly from the tutorial.
https://fastapi.tiangolo.com/
"""

from fastapi import FastAPI

from app.database import init_tortoise_fastapi
from app.routers import bahn, tracked_connections, authentication


app = FastAPI()
init_tortoise_fastapi(app)

app.include_router(
    prefix="/bahn",
    tags=["bahn"],
    router=bahn.router,
)
app.include_router(
    prefix="/tracking/connections",
    tags=["tracking"],
    router=tracked_connections.router,
)
app.include_router(
    prefix="/authentication",
    tags=["authentication"],
    router=authentication.router,
)
