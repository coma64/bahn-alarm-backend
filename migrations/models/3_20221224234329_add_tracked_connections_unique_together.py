from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE UNIQUE INDEX "uid_trackedconn_origin__57cbab" ON "trackedconnection" ("origin_station", "destination_station", "hours", "minutes");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX "uid_trackedconn_origin__57cbab";"""
