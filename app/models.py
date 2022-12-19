from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class User(models.Model):
    name = fields.CharField(max_length=255)
    tracked_connections: fields.ManyToManyRelation["TrackedConnection"]
    password_hash = fields.CharField(max_length=128)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    class PydanticMeta:
        exclude = ["password_hash"]


User_Pydantic = pydantic_model_creator(User, name="User")
UserIn_Pydantic = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)


class TrackedConnection(models.Model):
    tracked_by: fields.ManyToManyRelation[User] = fields.ManyToManyField(
        "models.User",
        related_name="tracked_connections",
        through="tracked_connection_users",
        on_delete=fields.CASCADE,
    )
    origin_station = fields.CharField(max_length=255)
    destination_station = fields.CharField(max_length=255)
    hours = fields.SmallIntField()
    minutes = fields.SmallIntField()


TrackedConnection_Pydantic = pydantic_model_creator(TrackedConnection, name="TrackedConnection")