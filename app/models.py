import typing as t
from datetime import datetime

from pydantic import BaseModel, Field
from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator

from app import authentication


class User(models.Model):
    name = fields.CharField(max_length=255, unique=True)
    tracked_connections: fields.ManyToManyRelation["TrackedConnection"]
    password_hash = fields.CharField(max_length=128)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    @classmethod
    async def login(cls, name: str, password: str) -> t.Union["User", None]:
        user = await cls.get_or_none(name=name)
        if not user:
            return

        if authentication.verify_password(password, user.password_hash):
            return user

    @classmethod
    async def authenticate(cls, token: str) -> t.Union["User", None]:
        username = authentication.get_username(token)
        if not username:
            return

        return await cls.get_or_none(name=username)

    @classmethod
    async def create(
        cls,
        using_db: models.BaseDBAsyncClient | None = None,
        *,
        password: str,
        **kwargs,
    ) -> "User":
        return await super().create(
            using_db,
            password_hash=authentication.hash_password(password),
            **kwargs,
        )

    def create_access_token(self) -> str:
        return authentication.create_access_token(self.name)

    async def set_password(self, password: str) -> None:
        self.password_hash = authentication.hash_password(password)
        await self.save()

    class PydanticMeta:
        exclude = ["password_hash"]


class TrackedConnection(models.Model):
    tracked_by: fields.ManyToManyRelation[User] = fields.ManyToManyField(
        "models.User",
        related_name="tracked_connections",
        through="tracked_connection_users",
        on_delete=fields.CASCADE,
    )
    origin_station: str = fields.CharField(max_length=255)
    destination_station: str = fields.CharField(max_length=255)
    hours: int = fields.SmallIntField()
    minutes: int = fields.SmallIntField()

    delay_info: fields.OneToOneRelation["ConnectionDelayInfo"]

    class Meta:
        unique_together = [
            ["origin_station", "destination_station", "hours", "minutes"]
        ]


class ConnectionDelayInfo(models.Model):
    tracked_connection: fields.OneToOneRelation[
        TrackedConnection
    ] = fields.OneToOneField(
        "models.TrackedConnection",
        related_name="delay_info",
        on_delete=fields.CASCADE,
    )
    is_on_time: bool = fields.BooleanField()
    is_canceled: bool = fields.BooleanField()
    delay_departure_minutes: int = fields.IntField()
    delay_arrival_minutes: int = fields.IntField()
    modified_at: datetime = fields.DatetimeField(auto_now=True)


def _create_partial_input_model(
    model: t.Type[models.Model],
    pydantic_input_model: t.Type[BaseModel],
) -> t.Type[BaseModel]:
    return pydantic_model_creator(
        model,
        name=f"{model.__name__}InPartial",
        exclude_readonly=True,
        optional=tuple(pydantic_input_model.__fields__.keys()),
    )


User_Pydantic = pydantic_model_creator(User, name="User")


class UserIn_Pydantic(
    pydantic_model_creator(User, name="UserIn", exclude_readonly=True)
):
    name: str = Field(..., min_length=3)
    password: str


TrackedConnection_Pydantic = pydantic_model_creator(
    TrackedConnection, name="TrackedConnection"
)
TrackedConnectionList_Pydantic = pydantic_queryset_creator(
    TrackedConnection, name="TrackedConnectionList"
)
TrackedConnectionIn_Pydantic = pydantic_model_creator(
    TrackedConnection, name="TrackedConnectionIn", exclude_readonly=True
)
TrackedConnectionInPartial_Pydantic = _create_partial_input_model(
    TrackedConnection, TrackedConnectionIn_Pydantic
)
