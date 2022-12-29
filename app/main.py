"""
Minimal FastAPI application taken directly from the tutorial.
https://fastapi.tiangolo.com/
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_tortoise_fastapi
from app.routers import bahn, tracked_connections, authentication


app = FastAPI()
init_tortoise_fastapi(app)

origins = ["http://localhost:8000", "http://localhost:5000", "http://localhost:4173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
