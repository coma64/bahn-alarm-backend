from fastapi import APIRouter
from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Q

from app import models
from app import responses

router = APIRouter()


@router.get("/{connection_id}", responses=responses.NOT_FOUND)
async def read(connection_id: int) -> models.TrackedConnection_Pydantic:
    try:
        return await models.TrackedConnection_Pydantic.from_queryset_single(
            models.TrackedConnection.get(id=connection_id)
        )
    except DoesNotExist as e:
        raise responses.NOT_FOUND_EXCEPTION from e


@router.get("", response_model=list[models.TrackedConnection_Pydantic])
async def read_list(
    name: str | None = None, offset: int = 0, limit: int = 50
) -> list[models.TrackedConnection_Pydantic]:
    connections = models.TrackedConnection.all().offset(offset).limit(limit)
    if name:
        connections = connections.filter(
            Q(origin_station__icontains=name) | Q(destination_station__icontains=name),
        )

    return await models.TrackedConnection_Pydantic.from_queryset(connections)


@router.post("")
async def create(
    connection: models.TrackedConnectionIn_Pydantic,
) -> models.TrackedConnection_Pydantic:
    model = await models.TrackedConnection.create(**connection.dict(exclude_unset=True))
    return await models.TrackedConnection_Pydantic.from_tortoise_orm(model)


@router.put("", responses=responses.NOT_FOUND)
async def update(
    connection_id: int, updates: models.TrackedConnectionIn_Pydantic
) -> models.TrackedConnection_Pydantic:
    try:
        connection = await models.TrackedConnection.get(id=connection_id)
        await connection.update_from_dict(updates.dict()).save()
        return await models.TrackedConnection_Pydantic.from_tortoise_orm(connection)
    except DoesNotExist as e:
        raise responses.NOT_FOUND_EXCEPTION from e


@router.patch("", responses=responses.NOT_FOUND)
async def partial_update(
    connection_id: int, connection: models.TrackedConnectionInPartial_Pydantic
) -> models.TrackedConnection_Pydantic:
    try:
        connection_object = await models.TrackedConnection.get(id=connection_id)
        await connection_object.update_from_dict(
            connection.dict(exclude_unset=True)
        ).save()
        return await models.TrackedConnection_Pydantic.from_tortoise_orm(
            connection_object
        )
    except DoesNotExist as e:
        raise responses.NOT_FOUND_EXCEPTION from e
