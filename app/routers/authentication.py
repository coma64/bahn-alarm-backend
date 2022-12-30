from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm

from app import models, responses, deps
from app.schemas import authentication as schemas

router = APIRouter()


@router.post(
    "/token",
    response_model=schemas.LoginResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": responses.HttpErrorModel},
    },
)
async def login(form: OAuth2PasswordRequestForm = Depends()) -> schemas.LoginResponse:
    user = await models.User.login(form.username, form.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return schemas.LoginResponse(access_token=user.create_access_token())


@router.post("/register", response_model=models.User_Pydantic)
async def register(user: models.UserIn_Pydantic) -> models.User_Pydantic:
    user_obj = await models.User.create(**user.dict(exclude_unset=True))
    return await models.User_Pydantic.from_tortoise_orm(user_obj)


@router.get("/me", response_model=models.User_Pydantic)
async def read_me(
    user: models.User = Depends(deps.get_current_user),
) -> models.User_Pydantic:
    return await models.User_Pydantic.from_tortoise_orm(user)


@router.get("/vapid-key", response_model=schemas.ReadVapidKeyResponse)
async def read_vapid_key() -> schemas.ReadVapidKeyResponse:
    return schemas.ReadVapidKeyResponse(
        key="BHYUgv9E9n6jHX9MHumIb8o6PiMiD-kDVsH2785lMGOjVIXXwT63bv-rH_zmrT7mpbm-3mIgz60r5_7Wp9Ttl8M"
    )


@router.post("/register-push-notifications", status_code=status.HTTP_204_NO_CONTENT)
async def register_push_notifications(
    subscription: dict = Body(), user: models.User = Depends(deps.get_current_user)
) -> None:
    await models.PushNotificationsSubscription.update_or_create(
        {"subscription": subscription}, user=user
    )
