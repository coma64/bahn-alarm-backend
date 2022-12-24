from fastapi import APIRouter, Depends, HTTPException, status
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
