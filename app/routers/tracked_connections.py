from fastapi import APIRouter, Depends, status
from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Q

from app import deps, models, responses
from app.tasks import tasks

router = APIRouter()


@router.get("/{connection_id}", responses=responses.NOT_FOUND)
async def read(
    connection_id: int, user: models.User = Depends(deps.get_current_user)
) -> models.TrackedConnection_Pydantic:
    try:
        return await models.TrackedConnection_Pydantic.from_queryset_single(
            models.TrackedConnection.filter(tracked_by=user).get(id=connection_id)
        )
    except DoesNotExist as e:
        raise responses.NOT_FOUND_EXCEPTION from e


@router.get("", response_model=list[models.TrackedConnection_Pydantic])
async def read_list(
    station: str | None = None, user: models.User = Depends(deps.get_current_user)
) -> list[models.TrackedConnection_Pydantic]:
    connections = models.TrackedConnection.filter(tracked_by=user)
    if station:
        connections = connections.filter(
            Q(origin_station__icontains=station)
            | Q(destination_station__icontains=station),
        )

    return await models.TrackedConnection_Pydantic.from_queryset(connections)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create(
    connection: models.TrackedConnectionIn_Pydantic,
    user: models.User = Depends(deps.get_current_user),
) -> None:
    obj, _ = await models.TrackedConnection.get_or_create(
        **connection.dict(exclude_unset=True)
    )
    await obj.tracked_by.add(user)

    tasks.fetch_connection_delay_infos.send([obj.pk])


@router.delete(
    "/{connection_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=responses.NOT_FOUND,
)
async def delete(
    connection_id: int, user: models.User = Depends(deps.get_current_user)
) -> None:
    try:
        obj = await models.TrackedConnection.get(pk=connection_id)
    except DoesNotExist as e:
        raise responses.NOT_FOUND_EXCEPTION from e

    await obj.tracked_by.remove(user)
    if await obj.tracked_by.all().count() == 0:
        await obj.delete()
