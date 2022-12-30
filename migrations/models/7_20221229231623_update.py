from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "pushnotificationssubscription" ADD "subscription" JSONB NOT NULL;
        ALTER TABLE "pushnotificationssubscription" DROP COLUMN "endpoint";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "pushnotificationssubscription" ADD "endpoint" TEXT NOT NULL;
        ALTER TABLE "pushnotificationssubscription" DROP COLUMN "subscription";"""
