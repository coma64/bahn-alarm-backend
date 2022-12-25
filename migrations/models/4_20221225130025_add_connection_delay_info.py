from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "connectiondelayinfo" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "is_on_time" BOOL NOT NULL,
    "is_canceled" BOOL NOT NULL,
    "delay_departure_minutes" INT NOT NULL,
    "delay_arrival_minutes" INT NOT NULL,
    "tracked_connection_id" INT NOT NULL UNIQUE REFERENCES "trackedconnection" ("id") ON DELETE CASCADE
);;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "connectiondelayinfo";"""
